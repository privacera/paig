import logging
from api.shield.utils.custom_exceptions import BadRequestException
from api.shield.factory.guardrail_service_factory import GuardrailServiceFactory
from api.shield.services.tenant_data_encryptor_service import TenantDataEncryptorService
from api.shield.presidio.presidio_anonymizer_engine import PresidioAnonymizerEngine
from api.shield.scanners.PIIScanner import PIIScanner
from api.shield.scanners.AWSBedrockGuardrailScanner import AWSBedrockGuardrailScanner
from api.shield.scanners.ToxicContentScanner import ToxicContentScanner
from api.shield.model.scanner_result import ScannerResult

logger = logging.getLogger(__name__)

anonymizer = PresidioAnonymizerEngine()

def process_guardrail_response(input_data: dict) -> dict:

    result = {
        "config_type": {},
        "guardrail_provider_details": {}
    }

    # Process guardrail configs
    for config in input_data.get("guardrail_configs", []):
        config_type = config["config_type"]

        if config_type not in result["config_type"]:
            result["config_type"][config_type] = {
                "configs": {},
                "response_message": config.get("response_message")
            }

        for sub_config in config["config_data"]["configs"]:
            config_tag = sub_config.get("category") or sub_config.get("type") or sub_config.get("term") or sub_config.get("topic")
            config_action = sub_config.get("action", "DENY") or sub_config.get("value")
            if config_tag:
                # Process regex
                if config_tag == "regex":
                    config_tag = sub_config.get("name")
                result["config_type"][config_type]["configs"][config_tag] = config_action
            # Process denied terms
            if config_type == "DENIED_TERMS":
                keywords = sub_config.get("keywords", [])
                for keyword in keywords:
                    result["config_type"][config_type]["configs"][keyword] = config_action

    # Process guardrail provider details
    provider_response = input_data.get("guardrail_provider_response", {})
    provider_details = input_data.get("guardrail_connection_details", {})

    if provider_response:
        for provider, response_data in provider_response.items():
            result["guardrail_provider_details"][provider] = {
                "guardrailId": response_data["response"].get("guardrailId"),
                "guardrailArn": response_data["response"].get("guardrailArn"),
                "version": response_data["response"].get("version")
            }

            # Merge provider connection details
            if provider_details:
                result["guardrail_provider_details"][provider].update({
                    "connection_details": provider_details
                })

    return result

async def get_guardrail_by_id(request: dict, tenant_id: str) -> dict:
    guardrail_id = request.get("guardrailId")
    guardrail_service_client = GuardrailServiceFactory().get_guardrail_service_client()
    response = await guardrail_service_client.get_guardrail_info_by_id(tenant_id, guardrail_id)
    return response

async def decrypted_connection_details(tenant_id: str, connection_details: dict):
    try:
        tenant_data_encryptor_service = TenantDataEncryptorService()
        await tenant_data_encryptor_service.decrypt_guardrail_connection_details(tenant_id, connection_details)
    except Exception as e:
        raise BadRequestException(
            f"Invalid guardrail connection details: {connection_details} for tenant {tenant_id}. Got error {e}")

async def do_test_guardrail(tenant_id: str, transformed_response: dict, message: str) -> list:

    final_result = [paig_guardrail_test(transformed_response, message)]
    if isinstance(final_result[0], dict) and "DENY" not in final_result[0].get("action", ""):
        test_aws_guardrail_result = await aws_guardrail_test(tenant_id, transformed_response, message)
        if test_aws_guardrail_result:
            final_result.append(test_aws_guardrail_result)

    for result in final_result:
        if result.get("action") == "DENY":
            return [result]
    return final_result

def paig_pii_guardrail_evaluation(sensitive_data_config: dict, traits: list) -> (list, dict):
    deny_policies_list = []
    redact_policies_dict = {}
    # evaluate the guardrail PII policies
    sensitive_data_policies = sensitive_data_config.get("configs", {})
    for key, value in sensitive_data_policies.items():
        if value == "DENY" and key in traits:
            deny_policies_list.append(key)
        elif value == "REDACT" and key in traits:
            redact_policies_dict.update({key: "<<"+key+">>"})

    return deny_policies_list, redact_policies_dict

def mask_message(message: str, redact_policies_dict: dict, analyzer_results: list) -> str:
    # check the scanner_result for analyzer results
    # update the input text message with redacted values
    custom_mask_analyzer_result = [x for x in analyzer_results if
                                   x.entity_type in redact_policies_dict.keys()]
    masked_message = anonymizer.mask(message, redact_policies_dict, custom_mask_analyzer_result)

    return masked_message

def merge_scanner_results(scanner_results: list) -> ScannerResult:
    traits = []
    analyzer_results = []
    for result in scanner_results:
        traits.extend(result.get_traits())
        analyzer_results.extend(result.get("analyzer_result", []))
    return ScannerResult(traits=sorted(traits), analyzer_result=analyzer_results)

def paig_guardrail_test(transformed_response: dict, message: str) -> dict:
    pii_scanner = PIIScanner(name="PIIScanner", model_path="_")
    pii_scanner_result = pii_scanner.scan(message)

    toxic_scanner = ToxicContentScanner(name="ToxicContentScanner", model_path="_", model_score_threshold=0.5, entity_type="TOXIC")
    toxic_scanner_result = toxic_scanner.scan(message)

    scanner_result = merge_scanner_results([pii_scanner_result, toxic_scanner_result])

    sensitive_data_config = transformed_response.get("config_type", {}).get("SENSITIVE_DATA", {})
    deny_policies_list, redact_policies_dict = paig_pii_guardrail_evaluation(sensitive_data_config, scanner_result.get_traits())

    if len(deny_policies_list) > 0:
        return {"action": "DENY", "tags": scanner_result.get_traits(), "policy": ["SENSITIVE_DATA"], "message": f'{sensitive_data_config.get("response_message")}'}

    if len(redact_policies_dict) > 0:
        masked_message = mask_message(message, redact_policies_dict, scanner_result.get("analyzer_result", []))
        return {"action": "REDACT", "tags": scanner_result.get_traits(), "policy": ["SENSITIVE_DATA"], "message": masked_message}

    return {"action": "ALLOW", "tags": scanner_result.get_traits(), "policy": ["SENSITIVE_DATA"], "message": message}

async def aws_guardrail_test(tenant_id: str, transformed_response: dict, message: str) -> None|dict:

    # check if AWS guardrail is present
    guardrail_provider_details = transformed_response.get("guardrail_provider_details", {})
    if not "AWS" in guardrail_provider_details:
        logger.debug("AWS Guardrail not configured. Hence skipping the AWS Guardrail test.")
        return {}

    aws_guardrail_details = guardrail_provider_details.get("AWS", {})
    aws_guardrail_id = aws_guardrail_details.get("guardrailId")
    aws_guardrail_version = aws_guardrail_details.get("version")
    aws_guardrail_region = "us-east-1"

    aws_guardrail_connection_details = aws_guardrail_details.get("connection_details", {})
    if aws_guardrail_connection_details:
        await decrypted_connection_details(tenant_id, aws_guardrail_connection_details)
        aws_guardrail_region = aws_guardrail_connection_details.get("region", "us-east-1")

    aws_guardrail_scanner_instance = AWSBedrockGuardrailScanner(guardrail_id=aws_guardrail_id,
                                                                  guardrail_version=aws_guardrail_version,
                                                                  region=aws_guardrail_region,
                                                                  connection_details=aws_guardrail_connection_details,
                                                                  scan_for_req_type="prompt")
    scanner_result = aws_guardrail_scanner_instance.scan(message)
    if scanner_result.get("actions"):
        policies_identified = []
        response_msg = ""
        scanner_result.get_traits().sort()
        for key, value in transformed_response.get("config_type", {}).items():
            for category, action in value.get("configs", {}).items():
                if category.replace(' ', '_').upper() in scanner_result.get_traits() and action == "DENY":
                    policies_identified.append(key)
                    if not response_msg:
                        response_msg = value.get("response_message")

        return {"action": "DENY", "tags": scanner_result.get_traits(), "policy": policies_identified, "message": response_msg }
