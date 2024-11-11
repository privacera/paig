import ast
import asyncio
import json
import logging
import os
import threading
import time
import traceback
from pathlib import Path

from api.shield.model.shield_audit import ShieldAuditViaApi
from api.shield.utils.custom_exceptions import ShieldException
from paig_common.encryption import DataEncryptor
from api.shield.model.encryption_key_info import EncryptionKeyInfo
from api.shield.model.authorize_response import AuthorizeResponse
from api.shield.utils import config_utils
from api.shield.model.authorize_request import AuthorizeRequest
from core.utils import Singleton

logger = logging.getLogger(__name__)


class ShieldDataEncryptor:

    def __init__(self, tenant_id, enable_background_key_refresh=True, account_service_client=None):
        logger.debug(
            f"==> {tenant_id} : ShieldDataEncryptor(tenant_id={tenant_id}, "
            f"enable_encryption_key_refresher={enable_background_key_refresh})")
        self.tenant_id = tenant_id
        self.shield_server_public_key_map = {}
        self.shield_server_private_key_map = {}
        self.shield_plugin_public_key_map = {}
        self.data_encryptor = None
        self.last_access_time = time.time()
        self.account_service_client = account_service_client
        self.enable_background_key_refresh = enable_background_key_refresh
        self.encryption_key_refresher = None

        logger.debug(
            f"<== ShieldDataEncryptor(tenant_id={tenant_id}, enable_encryption_key_refresher="
            f"{enable_background_key_refresh})")

    async def initialize_encryption_key_refresher(self, enable_background_key_refresh):
        self.enable_background_key_refresh = enable_background_key_refresh
        self.encryption_key_refresher = EncryptionKeyRefresher(self, self.account_service_client)
        if self.enable_background_key_refresh:
            await self.encryption_key_refresher.init_refresher()
            self.encryption_key_refresher.start()
        else:
            await self.encryption_key_refresher.download_and_refresh_key()

    def create_data_encryptor(self, encryption_key_id=-1):
        logger.debug(f"==> {self.tenant_id} : ShieldDataEncryptor::create_data_encryptor()")

        if encryption_key_id != -1:
            public_key = private_key = None
            if encryption_key_id in self.shield_plugin_public_key_map:
                public_key = self.shield_plugin_public_key_map[encryption_key_id]
            if encryption_key_id in self.shield_server_public_key_map:
                public_key = self.shield_server_public_key_map[encryption_key_id]
            if encryption_key_id in self.shield_server_private_key_map:
                private_key = self.shield_server_private_key_map[encryption_key_id]

            if public_key is None and private_key is None:
                raise ShieldException(
                    f"Encryption keys with id {encryption_key_id} not found for tenant {self.tenant_id}")
            self.data_encryptor = DataEncryptor(public_key=public_key, private_key=private_key)
        else:
            raise ValueError("Encryption key id cannot be -1")

        logger.debug(f"<== {self.tenant_id} : ShieldDataEncryptor::create_data_encryptor()")

    def encrypt(self, data):
        if self.data_encryptor is None:
            logger.error(f"Encryption keys not loaded for tenant = {self.tenant_id}")
            raise ShieldException()

        return self.data_encryptor.encrypt(data)

    def decrypt(self, data):
        if self.data_encryptor is None:
            logger.error(f"Encryption keys not loaded for tenant = {self.tenant_id}")
            raise ShieldException()

        return self.data_encryptor.decrypt(data)

    def cleanup(self):
        logger.debug(f"==> {self.tenant_id} : ShieldDataEncryptor::cleanup()")
        if self.enable_background_key_refresh:
            self.encryption_key_refresher.cleanup()
        logger.debug(f"<== {self.tenant_id} : ShieldDataEncryptor::cleanup()")


class EncryptionKeyRefresher:
    def __init__(self, data_encryptor: ShieldDataEncryptor, account_service_client=None):

        logger.debug(f"==> {data_encryptor.tenant_id} : EncryptionKeyRefresher({data_encryptor})")

        self.data_encryptor = data_encryptor
        self.exit_event = asyncio.Event()
        self.tenant_id = data_encryptor.tenant_id

        self.account_service_client = account_service_client

        encryption_keys_cache_dir = config_utils.get_property_value("encryption_keys_cache_dir", "/tmp/encrypt_cache")
        self.key_file_path = encryption_keys_cache_dir + f"/key_{self.tenant_id}.json"

        self.poll_interval_sec = config_utils.get_property_value_int("encryption_key_refresher_poll_interval_sec", 10)

        self.enable_encryption_keys_cache_dir = config_utils.get_property_value_boolean(
            "enable_encryption_keys_cache_dir")
        self.task = None
        logger.debug(f"<== {data_encryptor.tenant_id} : EncryptionKeyRefresher({data_encryptor})")

    async def init_refresher(self):
        logger.debug(f"==> {self.tenant_id} : EncryptionKeyRefresher::init_refresher()")

        if self.enable_encryption_keys_cache_dir:
            encryption_key_info_list = self.get_key_from_cache()
            if len(encryption_key_info_list) > 0:
                for encryption_key_info in encryption_key_info_list:
                    self.refresh_context_with_key_info(EncryptionKeyInfo(encryption_key_info))

        await self.download_and_refresh_key()

        logger.debug(f"<== {self.tenant_id} : EncryptionKeyRefresher::init_refresher()")

    async def async_run(self):
        logger.debug(f"==> {self.tenant_id} : EncryptionKeyRefresher::async_run() started")
        while not self.exit_event.is_set():
            await self.download_and_refresh_key()
            await asyncio.sleep(self.poll_interval_sec)

    def start(self):
        if self.task is None:
            logger.debug(f"{self.tenant_id} : EncryptionKeyRefresher::start() creating task")
            self.task = asyncio.create_task(self.async_run())

    def cleanup(self):
        logger.debug(f"==> {self.tenant_id} : EncryptionKeyRefresher::cleanup()")
        self.exit_event.set()
        logger.debug(f"<== {self.tenant_id} : EncryptionKeyRefresher::cleanup()")

    def get_key_from_cache(self):
        logger.debug(f"==> {self.tenant_id} : EncryptionKeyRefresher::get_key_from_cache()")
        encryption_key_info_list = []
        try:
            if os.path.exists(self.key_file_path) and os.path.getsize(self.key_file_path) > 0:
                with open(self.key_file_path, 'r') as key_file:
                    encryption_key_info_list = json.load(key_file)

        except Exception as e:
            stack_trace = traceback.format_exc()

            logger.error(
                "An error occurred when loading cached encryption key for tenant " + self.tenant_id + " : " + str(e))
            logger.error("Stack Trace:\n%s", stack_trace)

        logger.debug(f"<== {self.tenant_id} : EncryptionKeyRefresher::get_key_from_cache()")
        return encryption_key_info_list

    def store_key_to_cache(self, encryption_key_infos):
        logger.debug(f"==> {self.tenant_id} : EncryptionKeyRefresher::store_key_to_cache()")
        with open(self.key_file_path, 'w+') as key_file:
            json.dump(encryption_key_infos, key_file, indent=4)
        logger.debug(f"<== {self.tenant_id} : EncryptionKeyRefresher::store_key_to_cache()")

    def refresh_context_with_key_info(self, encryption_key_info):
        logger.debug(f"==> {self.tenant_id} : EncryptionKeyRefresher::refresh_context_with_key_info()")

        if encryption_key_info.keyType == "MSG_PROTECT_PLUGIN":
            self.data_encryptor.shield_plugin_public_key_map[
                encryption_key_info.id] = encryption_key_info.publicKeyValue
        else:
            self.data_encryptor.shield_server_public_key_map[
                encryption_key_info.id] = encryption_key_info.publicKeyValue
            self.data_encryptor.shield_server_private_key_map[
                encryption_key_info.id] = encryption_key_info.privateKeyValue

    async def download_and_refresh_key(self):
        logger.debug(f"==> {self.tenant_id} : EncryptionKeyRefresher::download_and_refresh_key()")

        # Load encryption keys from self_managed config properties
        plugin_public_keys, shield_private_keys, shield_public_keys = self.load_self_managed_encrypt_keys()
        # return if all keys are available else download from account service i.e. cloud mode
        if shield_private_keys and shield_public_keys and plugin_public_keys:
            return
        elif config_utils.get_property_value_boolean("load_encryption_keys_from_file"):
            logger.error(f"Encryption keys not found for tenant {self.tenant_id}!!")
            raise ShieldException(f"Error while loading encryption keys for tenant {self.tenant_id} in "
                                  f"self_managed mode. Please fix the self_managed "
                                  f"configuration file with all the required keys before starting shield server.")

        try:
            encryption_key_infos = await self.account_service_client.get_all_encryption_keys(self.tenant_id)

            if self.enable_encryption_keys_cache_dir:
                self.store_key_to_cache(encryption_key_infos)

            for encryption_key_info in encryption_key_infos:
                self.refresh_context_with_key_info(EncryptionKeyInfo(encryption_key_info))
        except Exception as e:
            logger.error(e)

        logger.debug(f"<== {self.tenant_id} : EncryptionKeyRefresher::download_and_refresh_key()")

    def load_self_managed_encrypt_keys(self):
        # following properties will be available in self_managed mode only
        plugin_public_keys = config_utils.get_property_value("plugin_public_key")
        self.load_key(plugin_public_keys, "plugin_public_key")
        shield_public_keys = config_utils.get_property_value("shield_public_key")
        self.load_key(shield_public_keys, "shield_public_key")
        shield_private_keys = config_utils.get_property_value("shield_private_key")
        self.load_key(shield_private_keys, "shield_private_key")
        return plugin_public_keys, shield_private_keys, shield_public_keys

    def load_key(self, config_encryption_keys_str, key_name):
        try:
            if config_encryption_keys_str is not None:
                config_encryption_keys = ast.literal_eval(config_encryption_keys_str)
                for key in config_encryption_keys:
                    for keyid, value in key.items():
                        self.update_key_map(key_name, keyid, value)
        except Exception as e:
            logger.error(f"Error while loading encryption key {key_name} from config file. {e}")
            raise ShieldException(f"Failed to load encryption key {key_name} from config file.")

    def update_key_map(self, key_name, keyid, value):
        if key_name == "plugin_public_key":
            self.data_encryptor.shield_plugin_public_key_map[int(keyid)] = value
        if key_name == "shield_public_key":
            self.data_encryptor.shield_server_public_key_map[int(keyid)] = value
        if key_name == "shield_private_key":
            self.data_encryptor.shield_server_private_key_map[int(keyid)] = value


class TenantDataEncryptorService(Singleton):

    def __init__(self, account_service_client=None):
        if self.is_instance_initialized():
            return

        logger.debug("==> TenantDataEncryptorService()")
        self.account_service_client = account_service_client
        self.max_idle_time = config_utils.get_property_value_int("tenant_data_encryptor_max_idle_time_sec", 120)
        self.tenant_data_encryptors = {}

        self.cleanup_interval_sec = config_utils.get_property_value_int("tenant_data_encryptor_cleanup_interval_sec",
                                                                        120)

        self.enable_encryption_keys_cache_dir = config_utils.get_property_value_boolean(
            "enable_encryption_keys_cache_dir")
        if self.enable_encryption_keys_cache_dir:
            encryption_keys_cache_dir = config_utils.get_property_value("encryption_keys_cache_dir")
            encryption_keys_cache_dir_path = Path(encryption_keys_cache_dir)
            encryption_keys_cache_dir_path.mkdir(parents=True, exist_ok=True)

        self.data_encryptors_cleanup_thread = threading.Thread(target=self.cleanup_idle_instances)
        self.data_encryptors_cleanup_thread.daemon = True
        self.data_encryptors_cleanup_thread_started = False

        logger.debug("<== TenantDataEncryptorService()")

    async def get_data_encryptor(self, tenant_id, encryption_key_id=None) -> ShieldDataEncryptor:
        logger.debug(
            f"==> TenantDataEncryptorService::get_data_encryptor_common(tenant_id={tenant_id}, encryption_key_id="
            f"{encryption_key_id})")
        current_time = time.time()

        provided_encryption_key_id = encryption_key_id if encryption_key_id is not None else -1

        if not self.data_encryptors_cleanup_thread_started:
            self.data_encryptors_cleanup_thread.start()
            self.data_encryptors_cleanup_thread_started = True

        encryptor_dict_key = f"{tenant_id}_{encryption_key_id}" if encryption_key_id is not None else tenant_id

        # Check if an instance already exists for the tenant
        if encryptor_dict_key in self.tenant_data_encryptors:
            shield_data_encryptor = self.tenant_data_encryptors[encryptor_dict_key]
            shield_data_encryptor.last_access_time = current_time
        else:
            logger.info(f"Creating new data encryptor instance for tenant = {tenant_id} with key = {encryption_key_id}")

            start_refresher = config_utils.get_property_value("shield_run_mode") == "cloud"
            shield_data_encryptor = ShieldDataEncryptor(tenant_id=tenant_id,
                                                        enable_background_key_refresh=start_refresher,
                                                        account_service_client=self.account_service_client)
            await shield_data_encryptor.initialize_encryption_key_refresher(start_refresher)
            shield_data_encryptor.create_data_encryptor(encryption_key_id=provided_encryption_key_id)
            shield_data_encryptor.last_access_time = current_time
            self.tenant_data_encryptors[encryptor_dict_key] = shield_data_encryptor

        logger.debug(
            f"<== TenantDataEncryptorService::get_data_encryptor_common(tenant_id={tenant_id}, "
            f"encryption_key_id={encryption_key_id})")

        return shield_data_encryptor

    def cleanup_idle_instances(self):
        logger.debug("==> TenantDataEncryptorService::cleanup_idle_instances()")
        while True:

            current_time = time.time()
            # Remove instances that have been idle for more than max_idle_time
            for tenant_id, shield_data_encryptor in list(self.tenant_data_encryptors.items()):
                if current_time - shield_data_encryptor.last_access_time > self.max_idle_time:
                    logger.info(f"Cleaning up data encryptor instance for tenant = {tenant_id}")
                    try:
                        shield_data_encryptor.cleanup()
                        del self.tenant_data_encryptors[tenant_id]
                    except Exception as ex:
                        logger.error(f"Error while cleaning up data_encryptor instance for tenant id = {tenant_id} "
                                     f"and exception = {ex}")

            time.sleep(self.cleanup_interval_sec)

    async def encrypt(self, tenant_id, data, encryption_key_id=None):
        data_encryptor = await self.get_data_encryptor(tenant_id, encryption_key_id)
        return data_encryptor.encrypt(data)

    async def decrypt(self, tenant_id, data, encryption_key_id=None):
        data_encryptor = await self.get_data_encryptor(tenant_id, encryption_key_id)
        return data_encryptor.decrypt(data)

    async def encrypt_shield_audit(self, audit_message, tenant_id, encryption_key_id):
        for message_object in audit_message:
            for key, value in message_object.items():
                if value is not None and key != "analyzerResult":
                    message_object[key] = await self.encrypt(tenant_id, value, encryption_key_id)

    async def decrypt_authorize_request(self, auth_request: AuthorizeRequest):
        decrypted_messages = []
        for message in auth_request.messages:
            decrypted_message = await self.decrypt(auth_request.tenant_id, message, auth_request.shield_server_key_id)
            decrypted_messages.append(decrypted_message)

        auth_request.messages = decrypted_messages

    async def decrypt_shield_audit(self, shield_audit: ShieldAuditViaApi):
        for message_object in shield_audit.messages:
            for key, value in message_object.items():
                if value is not None and key != "analyzerResult":
                    message_object[key] = await self.decrypt(shield_audit.tenantId, value, shield_audit.encryptionKeyId)

    async def encrypt_authorize_response(self, auth_request: AuthorizeRequest, auth_response: AuthorizeResponse):
        encrypted_messages = []
        for message in auth_response.responseMessages:
            message_copy = message.copy()
            message_copy["responseText"] = await self.encrypt(auth_request.tenant_id, message_copy["responseText"],
                                                              auth_request.shield_plugin_key_id)
            encrypted_messages.append(message_copy)

        auth_response.responseMessages = encrypted_messages
