import os
import logging
import sys
from paig_client import client as paig_shield_client
import paig_client.exception
from core import config
logger = logging.getLogger(__name__)

class PAIGShield:
    def __init__(self):
        self.paig_config_map = {}
        self.DISABLE_PAIG_SHIELD_PLUGIN_FLAG = (os.getenv('DISABLE_PAIG_SHIELD_PLUGIN', default='False').lower() in
                                           ['true', '1', 'yes'])

        self.config = config.Config
        self.ai_application_conf = self.config["AI_applications"]

    def setup_shield_client(self):
        if self.DISABLE_PAIG_SHIELD_PLUGIN_FLAG:
            logger.info("PAIG Shield plugin disabled by environment variable DISABLE_PAIG_SHIELD_PLUGIN=true")
        else:
            logger.info("PAIG Shield plugin enabled by environment variable DISABLE_PAIG_SHIELD_PLUGIN=false")
            try:
                paig_shield_client.setup(frameworks=self.ai_application_conf["shield_frameworks"])
            except paig_client.exception.AccessControlException as err:
                logger.error(f"PAIG Shield plugin setup failed with error {err}")
                if 'PAIG_API_KEY' in os.environ:
                    logger.error(f"Invalid PAIG_API_KEY key.")
                    sys.exit('PAIG Shield plugin setup failed. Please provide valid PAIG_API_KEY key.')
                elif 'PRIVACERA_SHIELD_CONF_FILE' in os.environ:
                    logger.error(f"PAIG Shield configuration file used is {os.environ['PRIVACERA_SHIELD_CONF_FILE']}")
                    sys.exit(f"PAIG Shield plugin setup failed. Please confirm if the configuration file {os.environ['PRIVACERA_SHIELD_CONF_FILE']} is correct and exists")
    def get_paig_config_map(self, ai_application_name):
        return self.paig_config_map.get(ai_application_name)

    def paig_shield_setup_app_with_file(self, ai_application_name, paig_shield_config_file, app_count):
        """Handles PAIG Shield setup using a configuration file."""
        if not paig_shield_config_file:
            if app_count > 1:
                logger.error(f"AI Application {ai_application_name} missing required 'paig_api_key' or 'paig_shield_config_file' in configuration file")
                sys.exit(f"AI Application {ai_application_name} missing required 'paig_api_key' or 'paig_shield_config_file' configuration file")
            if 'PRIVACERA_SHIELD_CONF_FILE' in os.environ:
                logger.info(f"AI Application {ai_application_name} setup using 'PRIVACERA_SHIELD_CONF_FILE' environment variable")
                return
            logger.error("Missing shield config file / paig api key.")
            sys.exit("Missing shield config file / paig api key.")

        if not os.path.isfile(paig_shield_config_file):
            logger.error(
                f"paig_shield_config_file {paig_shield_config_file} does not exist in {ai_application_name} configuration")
            sys.exit(
                f"paig_shield_config_file {paig_shield_config_file} does not exist in {ai_application_name} configuration")

        try:
            ai_app = paig_shield_client.setup_app(application_config_file=paig_shield_config_file)
            self.paig_config_map[ai_application_name] = ai_app
        except paig_client.exception.AccessControlException as err:
            logger.error(f"PAIG Shield plugin setup failed for {ai_application_name} with error {err}")
            sys.exit(f"PAIG Shield plugin setup failed for {ai_application_name} with error {err}")

    def set_paig_config_map(self, ai_application_name, ai_application_config, app_count):
        """Sets up PAIG Shield configuration using either API key or config file."""
        paig_api_key = ai_application_config.get('paig_api_key')

        if paig_api_key:
            try:
                ai_app = paig_shield_client.setup_app(application_config_api_key=paig_api_key)
                self.paig_config_map[ai_application_name] = ai_app
            except paig_client.exception.AccessControlException as err:
                logger.error(f"PAIG Shield plugin setup failed for {ai_application_name} with error {err}")
                sys.exit(f"PAIG Shield plugin setup failed for {ai_application_name} with error {err}")
            return

        if app_count == 1 and 'PAIG_API_KEY' in os.environ:
            logger.info(f"AI Application {ai_application_name} setup using 'PAIG_API_KEY' environment variable")
            return

        logger.info("'paig_api_key' is not provided in config. Trying to setup PAIG Shield using configuration file.")
        self.paig_shield_setup_app_with_file(ai_application_name, ai_application_config.get('paig_shield_config_file'), app_count)