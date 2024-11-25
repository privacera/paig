import copy
import json
import logging
import time
import traceback

from api.shield.enum.ShieldEnums import Guardrail
from api.shield.factory.account_service_factory import AccountServiceFactory
from api.shield.factory.authz_service_client_factory import AuthzServiceClientFactory
from api.shield.logfile.audit_loggers import FluentdAuditLogger
from api.shield.services.application_manager_service import ApplicationManager
from api.shield.presidio.nlp_handler import NLPHandler
from api.shield.presidio.presidio_anonymizer_engine import PresidioAnonymizerEngine
from api.shield.utils import config_utils
from api.shield.model.authorize_request import AuthorizeRequest
from api.shield.model.authorize_response import AuthorizeResponse
from api.shield.model.authz_service_request import AuthzServiceRequest
from api.shield.model.authz_service_response import AuthzServiceResponse
from api.shield.model.vectordb_authz_request import AuthorizeVectorDBRequest
from api.shield.model.shield_audit import ShieldAudit
from api.shield.client.http_fluentd_client import FluentdRestHttpClient

from api.shield.services.tenant_data_encryptor_service import TenantDataEncryptorService
from api.shield.utils.custom_exceptions import ShieldException
from api.shield.utils import json_utils
from api.shield.logfile.log_message_in_s3 import LogMessageInS3File
from api.shield.logfile.log_message_in_local import LogMessageInLocal
from paig_common.paig_exception import DiskFullException, AuditEventQueueFullException
from api.shield.factory.governance_service_factory import GovernanceServiceFactory
from opentelemetry import metrics

from core.utils import SingletonDepends

logger = logging.getLogger(__name__)
meter = metrics.get_meter(__name__)


class AuthService:
    """
    Handles authorization and auditing processes for requests.

    This service is responsible for decrypting requests, analyzing messages, performing authorization,
    masking messages based on authorization results, encrypting responses, and logging audit events.
    It uses various dependencies and services, such as NLP handling, anonymization, and encryption.

    """

    def __init__(self):
        """
        Initializes the AuthService class with various dependencies and configuration settings.

        This constructor sets up the AuthService by initializing components such as NLP handler,
        application manager, authorization service client, account service client, and others.
        It also configures logging, encryption, and audit settings based on the provided configuration.
        """
        logger.debug("Initializing AuthService...")

        self._shield_run_mode = config_utils.get_property_value('shield_run_mode', 'cloud')

        self.nlp_handler = NLPHandler()
        self.application_manager = ApplicationManager()
        authz_service_client_factory = SingletonDepends(AuthzServiceClientFactory)
        self.authz_service_client = authz_service_client_factory.get_authz_service_client()
        account_service_factory: AccountServiceFactory = SingletonDepends(AccountServiceFactory)
        self.account_service_client = account_service_factory.get_account_service_client()
        governance_service_factory: GovernanceServiceFactory = SingletonDepends(GovernanceServiceFactory)
        self.governance_service_client = governance_service_factory.get_governance_service_client()
        self.fluentd_logger_client = FluentdRestHttpClient()
        self.tenant_data_encryptor_service = TenantDataEncryptorService(self.account_service_client)
        self.presidio_anonymizer_engine = PresidioAnonymizerEngine()

        self.access_log_timing_message = ""
        self.auth_req_context = {}
        self.message_log_objs = []
        self.fluentd_audit_logger = None
        self.audit_spool_dir = config_utils.get_property_value("audit_spool_dir", "/workdir/shield/audit-spool")
        self.init_log_message_in_file()
        self.fluentd_failure_counter = meter.create_counter(
            name="fluentd_failure_total",
            description="Count of Fluentd failures while logging audits",
            unit="1"
        )

        self.ignore_access_control_application_keys = config_utils.get_property_value_list("ignore_access_control_application_keys", [])
        logger.info("Found ignore_access_control_application_keys = " + str(self.ignore_access_control_application_keys))

        logger.info(f"AuthService Initialized in {self._shield_run_mode} mode!")

    async def authorize(self, auth_req: AuthorizeRequest):
        """
        Authorizes a request by processing and analyzing the authorization request, performing
        access control checks, masking sensitive information, and logging audit data.

        Returns:
            AuthorizeResponse: The response object containing the authorization result and masked messages.

        """
        authorize_start_time = time.perf_counter()
        masked_messages = []
        original_masked_text_list = []
        all_result_traits = set()
        access_control_traits = set()
        analyzer_result_map = {}
        self.auth_req_context = auth_req.context

        # Decrypt authorize request
        decrypt_start_time = time.perf_counter()
        await self.tenant_data_encryptor_service.decrypt_authorize_request(auth_req)
        logger.debug("Auth Request After Decrypt : " + json_utils.mask_json_fields(json.dumps(auth_req.__dict__),
                                                                                   ['messages']))
        decrypt_time = f"{((time.perf_counter() - decrypt_start_time) * 1000):.3f}"
        
        gov_result = await self.governance_service_client.get_aws_bedrock_guardrail_info(auth_req.tenant_id, auth_req.application_key)
        auth_req.context.update(gov_result)

        # loop through the messages in request to scan for traits
        message_analyze_start_time = time.perf_counter()
        scan_timings_per_message = self.analyze_scan_messages(access_control_traits, all_result_traits,
                                                              analyzer_result_map, auth_req, True)
        message_analyze_time = f"{((time.perf_counter() - message_analyze_start_time) * 1000):.3f}"
        logger.debug(f"All resulted tags from input text {all_result_traits}")

        # authorize traits
        authz_start_time = time.perf_counter()
        logger.debug(f"Calling authz service with request: {auth_req} "
                     f"with traits for access control: {all_result_traits}")
        authz_service_res = await self.do_authz_authorize(auth_req, list(all_result_traits))
        authz_time = f"{((time.perf_counter() - authz_start_time) * 1000):.3f}"
        logger.debug(f"Received authz service response: {authz_service_res.__dict__}")
        is_allowed = authz_service_res.authorized

        # process for non authz scanners
        non_authz_scan_timings_per_message = 0
        if is_allowed:
            non_authz_scan_timings_per_message = self.analyze_scan_messages(access_control_traits, all_result_traits,
                                                                            analyzer_result_map, auth_req, False)

            if Guardrail.BLOCKED.value in access_control_traits:
                authz_service_res.authorized = is_allowed = False
                authz_service_res.status_message = self.generate_access_denied_message(all_result_traits)

                logger.debug(f"Non Authz scanner blocked the request with all tags: {all_result_traits} and actions: {access_control_traits}")

        # Overriding the access control results for the application keys configured under
        # property ignore_access_control_application_keys
        if auth_req.application_key in self.ignore_access_control_application_keys:
            logger.info(f"Overriding access control results for application_key=" + auth_req.application_key)
            authz_service_res.authorized = is_allowed = True
            authz_service_res.masked_traits = {}
            masked_messages = []

        masking_start_time = time.perf_counter()
        # post authz process i.e masking the message
        self.post_authz_process(analyzer_result_map, auth_req, authz_service_res, masked_messages, original_masked_text_list)
        masking_time = f"{((time.perf_counter() - masking_start_time) * 1000):.3f}"

        # encrypt the message
        await self.tenant_data_encryptor_service.encrypt_shield_audit(original_masked_text_list,
                                                                      tenant_id=auth_req.tenant_id,
                                                                      encryption_key_id=auth_req.shield_server_key_id)
        logger.debug("Encrypted the message before shield audit object creation")

        # log audit
        all_result_traits = sorted(all_result_traits)
        shield_audit = ShieldAudit(auth_req, authz_service_res, all_result_traits, original_masked_text_list)
        audit_cloud_time, audit_self_managed_time = 0, 0
        if auth_req.enable_audit is None or auth_req.enable_audit:
            # audit the message to fluentd or S3
            audit_cloud_time, audit_self_managed_time = await self.audit(shield_audit)

        logger.debug("Completed audit logging")
        # Updating Authorize response Object response_messages with the data required by plugin in case of
        # streaming.
        self.enrich_auth_response(authz_service_res, masked_messages, all_result_traits)

        # process authorize response
        auth_response = AuthorizeResponse(is_allowed=is_allowed, response_messages=masked_messages, auth_req=auth_req)
        # Encrypt the response messages with plugin's provided public key
        encrypt_start_time = time.perf_counter()
        if auth_response.isAllowed:
            await self.tenant_data_encryptor_service.encrypt_authorize_response(auth_req, auth_response)
            logger.debug("Auth Response After Encrypt : " + json_utils.mask_json_fields(
                json.dumps(auth_response.__dict__),
                ['responseMessages']))
        encrypt_time = f"{((time.perf_counter() - encrypt_start_time) * 1000):.3f}"

        authorize_total_time = f"{((time.perf_counter() - authorize_start_time) * 1000):.3f}"
        self.access_log_timing_message = (f" Total time= {authorize_total_time}ms, "
                                          f"Decryption time= {decrypt_time}ms, Message analysis time= {message_analyze_time}ms, "
                                          f"Authz authorization time = {authz_time}ms, Masking time= {masking_time}ms, "
                                          f"Encryption time= {encrypt_time}ms, Audit Cloud time= {audit_cloud_time}ms ,"
                                          f"Audit Self managed time= {audit_self_managed_time}ms ,"
                                          f"Message Scan timings= {scan_timings_per_message}ms, "
                                          f"Non Authz Message Scan timings= {non_authz_scan_timings_per_message}ms")

        return auth_response

    def post_authz_process(self, analyzer_result_map, auth_req, authz_service_res, masked_messages,
                           original_masked_text_list):
        """
        Processes the authorization response by either masking the request messages or appending an error message
        based on the authorization result.

        """
        for request_text in auth_req.messages:
            self.process_masking(analyzer_result_map.get(request_text, []), request_text, authz_service_res,
                                    masked_messages,
                                    original_masked_text_list)

    def analyze_scan_messages(self, access_control_traits, all_result_traits, analyzer_result_map, auth_req,
                              is_authz_scan):
        """
        Analyzes the messages in the authorization request to extract traits and generate scan results.

        Returns:
            list: A list of dictionaries where each dictionary contains the scan timings for a message, with each
                  dictionary keyed by scanner names and their respective scan timings in milliseconds.
        """
        scan_timings_per_message = []
        for request_text in auth_req.messages:
            # Analyze traits
            scanners_result, message_scan_timings = self.application_manager.scan_messages(
                request_text, auth_req, is_authz_scan)
            scan_timings = {scanner_name: f"{message_scan_time}ms" for scanner_name, message_scan_time in
                            message_scan_timings.items()}

            scan_timings_per_message.append(scan_timings)
            # Update the set with traits and store analyzer results if present
            scanner_analyzer_results = analyzer_result_map.get(request_text, [])
            for scanner_data in scanners_result.values():
                all_result_traits.update(scanner_data.get_traits())
                scanner_analyzer_results.extend(scanner_data.get("analyzer_result", []))
                access_control_traits.update(scanner_data.get("actions", []))

            analyzer_result_map[request_text] = scanner_analyzer_results

        return scan_timings_per_message

    @staticmethod
    def enrich_auth_response(authz_service_res, masked_messages, traits):
        """
         Enriches each message in the `masked_messages` list with additional information from the `authz_service_res` object
         and the provided `traits`.

        """
        for msg in masked_messages:
            msg.update({"traits": traits,
                        "maskedTraits": authz_service_res.masked_traits,
                        "rangerAuditIds": authz_service_res.ranger_audit_ids,
                        "rangerPolicyIds": authz_service_res.ranger_policy_ids,
                        "paigPolicyIds": authz_service_res.paig_policy_ids,
                        "applicationName": authz_service_res.application_name})

    async def audit(self, shield_audit):
        """
          Performs audit logging for the provided `shield_audit` object, logging both to a self-managed system and to a cloud-based
          Fluentd service.

          The method measures the time taken for each logging process and returns these timings.

          Returns:
              tuple: A tuple containing two elements:
                  - audit_cloud_time (str): The time taken to log to the cloud-based Fluentd service, formatted as a string in milliseconds.
                  - audit_self_managed_time (str): The time taken to log to the self-managed system, formatted as a string in milliseconds.
        """
        audit_self_managed_start_time = time.perf_counter()
        await self.log_audit_message(shield_audit)
        audit_self_managed_time = f"{((time.perf_counter() - audit_self_managed_start_time) * 1000):.3f}"
        audit_cloud_start_time = time.perf_counter()
        audit_msg_content_storage_system = config_utils.get_property_value_list("audit_msg_content_storage_system")
        """
        This section handles the configuration of audit message content and metadata storage across different deployment modes.
        
        - **Case 1: Cloud Mode**  
          - `audit_msg_content_storage_system` is set to `fluentd`.
          - In this mode, the entire audit (both content and metadata) is sent to OpenSearch via Fluentd.
          - `default_msg_metadata_storage_system` can be left blank or also set to `fluentd`.
        
        - **Case 2: Self-Managed Mode (Docker)**  
          - `audit_msg_content_storage_system` is user-configurable and may be set to `s3` or `local`.
          - In this mode, only the metadata is sent to Fluentd, while the original message content is stored in the user-specified system (e.g., S3 or local storage).
          - `default_msg_metadata_storage_system` is added to ensure that metadata is still pushed to OpenSearch, even when Fluentd is not the primary content storage.
        
        - **Case 3: Self-Managed Mode (OpenSource)**  
          - `audit_msg_content_storage_system` is set to `data-service`.
          - In this mode, `default_msg_metadata_storage_system` can be left blank since Data-Service will handle the audit storage and no push to OpenSearch via Fluentd is required.
        
        This logic ensures that audit metadata is correctly routed based on the deployment mode, with special handling to push metadata to OpenSearch in self-managed environments.
        """
        default_msg_metadata_storage_system = config_utils.get_property_value_list("default_msg_metadata_storage_system")
        if "fluentd" in audit_msg_content_storage_system or "fluentd" in default_msg_metadata_storage_system:
            self.log_audit_fluentd(copy.deepcopy(shield_audit))
        audit_cloud_time = f"{((time.perf_counter() - audit_cloud_start_time) * 1000):.3f}"
        return audit_cloud_time, audit_self_managed_time

    async def audit_stream_data(self, shield_audit):
        """
        Performs decryption and encryption of the provided `shield_audit` object and then logs the audit data.

        """
        await self.tenant_data_encryptor_service.decrypt_shield_audit(shield_audit)
        await self.tenant_data_encryptor_service.encrypt_shield_audit(shield_audit.messages,
                                                                      tenant_id=shield_audit.tenantId,
                                                                      encryption_key_id=shield_audit.encryptionKeyId)

        await self.audit(shield_audit)

    async def do_authz_authorize(self, auth_req: AuthorizeRequest, result_entities):
        """
        Sends an authorization request to the authorization service client.

        This method creates an `AuthzServiceRequest` object using the provided `auth_req` and `result_entities`,
        and then sends it to the authorization service client for authorization.

        Returns:
            AuthzServiceResponse: The response from the authorization service client indicating whether the request is authorized.

        """
        authz_service_req = AuthzServiceRequest(auth_req=auth_req, traits=result_entities)
        return await self.authz_service_client.post_authorize(authz_service_req, auth_req.tenant_id)

    def process_masking(self, analyzer_result, request_text, authz_service_res: AuthzServiceResponse, masked_messages,
                        original_masked_text_list):
        """
        Processes and masks sensitive information in the request text based on the authorization response.

        This method handles the masking of sensitive information identified in the request text.
        It utilizes the Presidio Anonymizer Engine to mask entities as specified by the authorization service response.
        The results are added to `masked_messages` and `original_masked_text_list`.
        """
        logger.debug("Masking process started")
        masking_list = authz_service_res.masked_traits
        final_analyzer_result = self.process_and_convert_analyzer_result(analyzer_result)

        if masking_list:
            entities_with_custom_masked_value = masking_list
            analyzer_results_with_custom_mask_entities = [x for x in analyzer_result if
                                                          x.entity_type in entities_with_custom_masked_value]

            logger.debug(f"analyzer_results_with_custom_mask_entities: "
                         f"{set([x.entity_type for x in analyzer_results_with_custom_mask_entities])}")

            if analyzer_results_with_custom_mask_entities:
                masked_text = self.presidio_anonymizer_engine.mask(request_text, entities_with_custom_masked_value,
                                                                   analyzer_results_with_custom_mask_entities)
                masked_messages.append(dict(responseText=masked_text, analyzerResult=final_analyzer_result))
                original_masked_text_list.append(dict(originalMessage=request_text, maskedMessage=masked_text,
                                                      analyzerResult=json.dumps(final_analyzer_result)))
                logger.debug("Masking process finished")
                return
        if authz_service_res.authorized:
            masked_messages.append(dict(responseText=request_text, analyzerResult=final_analyzer_result))
        else:
            masked_messages.append(dict(responseText=authz_service_res.status_message))
        original_masked_text_list.append(dict(originalMessage=request_text, maskedMessage="",
                                              analyzerResult=json.dumps(final_analyzer_result)))

        logger.debug("Masking process finished")

    def process_and_convert_analyzer_result(self, analyzer_result):
        """
        Processes and converts the analyzer results to adjust entity positions and prepare them for JSON serialization.

        This method adjusts the start and end positions of each entity in the `analyzer_result` based on the
        `previous_sentence_length` from the authorization request context. It then converts the adjusted results
        into a JSON-serializable format.
        """
        analyzer_result_copy = copy.deepcopy(analyzer_result)
        previous_sentence_length = self.auth_req_context.get('previous_sentence_length', 0)

        result_json_list = []
        for result in analyzer_result_copy:
            result.start += previous_sentence_length
            result.end += previous_sentence_length
            result_json_list.append(result.__dict__)

        return result_json_list

    def log_audit_fluentd(self, shield_audit: ShieldAudit):
        """
        Logs audit messages to Fluentd with masking and error handling.

        This method logs audit messages to Fluentd, masking sensitive fields if necessary. It handles various
        exceptions that may occur during the logging process, such as disk full errors or audit event queue full
        errors. If logging fails and the audit failure error is enabled, appropriate exceptions are raised.

        Args:
            shield_audit (ShieldAudit): The audit data to be logged.

        Raises:
            ShieldException: If there is no space left on the device, the audit event queue is full, or logging fails
            due to other reasons and audit failure error is enabled.
       """

        audit_msg_content_to_paig_cloud = config_utils.get_property_value_boolean("audit_msg_content_to_paig_cloud",
                                                                                  False)
        if audit_msg_content_to_paig_cloud is False:
            masked_audit_obj = json_utils.mask_json_fields(json.dumps(shield_audit.__dict__),
                                                           ['originalMessage', 'maskedMessage'], "")
            shield_audit.__dict__ = json.loads(masked_audit_obj)

        fluentd_audit_logger = self.get_or_create_fluentd_audit_logger()
        fluentd_failure_enabled = config_utils.get_property_value_boolean("audit_failure_error_enabled", True)
        try:
            fluentd_audit_logger.log(shield_audit)
        except DiskFullException:
            if fluentd_failure_enabled is True:
                self.fluentd_failure_counter.add(1)
                raise ShieldException("No space left on device. Disk is full. Please increase the disk size or free "
                                      "up some space to push audits successfully.")
        except AuditEventQueueFullException:
            if fluentd_failure_enabled is True:
                self.fluentd_failure_counter.add(1)
                raise ShieldException("Audit event queue is full.The push rate is too high for the audit "
                                      "spooler to process.")
        except Exception as e:
            logger.error(
                f"Error logging audit message to fluentd: {type(e).__name__}: {str(e)} \n{traceback.format_exc()}")
            if fluentd_failure_enabled is True:
                self.fluentd_failure_counter.add(1)
                raise ShieldException("Failed to log audit record!")

    async def log_audit_message(self, log_data: ShieldAudit):
        """
        Asynchronously logs audit data using all available message loggers.

        This method iterates through all message log objects stored in `self.message_log_objs` and logs the
        provided audit data using each logger. The logging is performed asynchronously.
        """
        if len(self.message_log_objs) > 0:
            for message_log_obj in self.message_log_objs:
                await message_log_obj.log_audit_event(log_data)

    async def authorize_vectordb(self, vectordb_auth_req: AuthorizeVectorDBRequest, tenant_id: str):
        """
        Asynchronously authorizes a VectorDB request using the authorization service client.

        This method sends an authorization request for a VectorDB operation to the authorization service client and
        logs the request and response for debugging purposes.

        Returns:
            AuthzServiceResponse: The response from the authorization service client containing the authorization result.
        """

        logger.debug(f"Authz VectorDB authorization request: {vectordb_auth_req}")
        vectordb_auth_res = await self.authz_service_client.post_authorize_vectordb(vectordb_auth_req, tenant_id)
        logger.debug(f"Authz VectorDB authorization response: {vectordb_auth_res.__dict__}")
        return vectordb_auth_res

    def init_log_message_in_file(self):
        """
        Initializes log message handlers based on configuration settings for self-managed or customer-hosted modes.

        This method reads the configuration properties to determine whether to enable logging of audit messages to
        self-managed storage systems and initializes the appropriate log message handlers (local, S3, data-service)
        based on the specified storage systems in the configuration.

        Raises:
            ShieldException: If an invalid storage system is specified in the configuration.
        """
        audit_msg_content_to_self_managed_storage = config_utils.get_property_value_boolean(
            "audit_msg_content_to_self_managed_storage", True)
        audit_msg_content_storage_system_list = config_utils.get_property_value_list("audit_msg_content_storage_system",
                                                                                     "local")

        if ((self._shield_run_mode == 'self_managed' or self._shield_run_mode == 'customer_hosted')
                and audit_msg_content_to_self_managed_storage):
            for audit_msg_content_storage_system in audit_msg_content_storage_system_list:
                match audit_msg_content_storage_system.strip():
                    case "local":
                        self.message_log_objs.append(LogMessageInLocal())
                    case "s3":
                        self.message_log_objs.append(LogMessageInS3File())
                    case "data-service":
                        from api.audit.controllers.data_store_controller import DataStoreController
                        from api.shield.logfile.log_message_in_data_service import LogMessageInDataService
                        self.message_log_objs.append(LogMessageInDataService(SingletonDepends(DataStoreController)))
                    case _:
                        logger.error(f"Invalid audit_msg_content_storage_system: {audit_msg_content_storage_system}")
                        raise ShieldException(
                            f"Invalid message content storage system provided: {audit_msg_content_storage_system} ,"
                            f"Please Choose the correct storage system which is supported using "
                            f"audit_msg_content_storage_system property.")
            logger.debug(f"Initialized self-managed storage loggers: {self.message_log_objs}")

    def get_or_create_fluentd_audit_logger(self):
        """
        Get or create fluentd audit logger
        :return:
        """
        audit_event_queue_timeout_sec = config_utils.get_property_value_int("audit_event_queue_timeout_sec", 5)
        max_queue_size = config_utils.get_property_value_int("audit_event_queue_max_size", 0)
        if self.fluentd_audit_logger is None:
            self.fluentd_audit_logger = FluentdAuditLogger(self.fluentd_logger_client, self.audit_spool_dir,
                                                           max_queue_size,
                                                           audit_event_queue_timeout_sec)
            self.fluentd_audit_logger.daemon = True
            self.fluentd_audit_logger.start()

        return self.fluentd_audit_logger
    
    def generate_access_denied_message(self, all_traits: set) -> str:
        """
        Generates an access denied message based on the provided traits.

        This method generates an access denied message based on the provided traits. It constructs a message
        indicating that the request was denied due to the presence of certain traits.

        Args:
            all_traits (set): A set of traits that were detected in the request.

        Returns:
            str: The access denied message indicating the reason for the denial.
        """
        multi_trait_message = config_utils.get_property_value("default_access_denied_message_multi_trait",
                                                                        "Access is denied for ")
        mapped_messages = []
        for trait in all_traits:
            custom_text_message = config_utils.get_property_value(trait, None)
            if custom_text_message:
                mapped_messages.append(custom_text_message)
            else:
                mapped_messages.append(trait)

        if len(mapped_messages) == 1:
            response_text_message = f'{multi_trait_message} {mapped_messages[0]}'
        elif len(mapped_messages) > 1:
            response_text_message = f'{multi_trait_message} {", ".join(mapped_messages[:-1])} or {mapped_messages[-1]}'
        else:
            response_text_message = config_utils.get_property_value("default_access_denied_message",
                                                                    "Access is denied")

        return response_text_message
