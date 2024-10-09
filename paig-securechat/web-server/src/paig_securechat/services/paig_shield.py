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
                if 'PRIVACERA_SHIELD_CONF_FILE' in os.environ:
                    logger.info(f"PAIG Shield configuration file used is {os.environ['PRIVACERA_SHIELD_CONF_FILE']}")
                    sys.exit('PAIG Shield plugin setup failed. Please confirm if the configuration file {} is correct and '
                             'exists'.format(os.environ['PRIVACERA_SHIELD_CONF_FILE']))

    def get_paig_config_map(self, ai_application_name):
        return self.paig_config_map.get(ai_application_name)

    def set_paig_config_map(self, ai_application_name, ai_application_config):
        if 'paig_shield_config_file' not in ai_application_config:
            logger.info(f"paig_shield_config_file is missing in {ai_application_name} configuration")
            return None
        paig_shield_config_file = ai_application_config.get('paig_shield_config_file')
        if not os.path.isfile(paig_shield_config_file):
            logger.error(f"paig_shield_config_file {paig_shield_config_file} does not exist found in {ai_application_name} configuration")
            sys.exit(f"paig_shield_config_file {paig_shield_config_file} does not exist found  in {ai_application_name} configuration")
        try:
            ai_app = paig_shield_client.setup_app(application_config_file=paig_shield_config_file)
            self.paig_config_map[ai_application_name] = ai_app
        except paig_client.exception.AccessControlException as err:
            logger.error(f"PAIG Shield plugin setup failed for {ai_application_name}  with error {err}")
            sys.exit(f"PAIG Shield plugin setup failed for {ai_application_name}  with error {err}")