import importlib
import json
import logging
import sys
import os
from core import llm_constants
logger = logging.getLogger(__name__)


class AIApplications:

    def __init__(self, config):
        self.AI_applications= []
        self.impl_map = {}
        self.AI_applications_from_file = {}

        self.cnf = config
        if 'AI_applications' not in self.cnf:
            sys.exit("AI_applications key is missing from configuration file.Please add AI_applications configuration.")
        if 'file_path' not in self.cnf['AI_applications']:
            sys.exit("file_path key is missing from configuration file.Please add file_path in configuration.")
        file_path = self.cnf['AI_applications']['file_path']
        if not os.path.isfile(file_path):
            sys.exit("AI_applications file does not exist. File Path :- " + str(file_path))
        with open(file_path, 'r') as file:
            logger.info('Open AI_applications files :- ' + str(file_path))
            try:
                self.AI_applications_from_file = json.load(file)
            except Exception as e:
                logger.error("Error in loading AI_applications file " + str(e))
            self.AI_applications= [AI_application for AI_application in self.AI_applications_from_file.get("AI_applications") if AI_application.get("enable")]

        self.create_instances()

    def get_AI_applications(self):
        return self.AI_applications

    def get_AI_applications_for_ui(self):
        return self.AI_applications_from_file

    def create_instances(self):
        logger.info(f"create_instances AI_applications={self.AI_applications}")

        for AI_application in self.AI_applications:
            ai_application_name = AI_application.get("name")
            if not AI_application.get("enable"):
                logger.info(f"skipping disabled AI_application, name={ai_application_name}")
                continue
            logger.info(f"Instantiating AI_application {ai_application_name} ...")
            impl_class = self.cnf['AI_applications'].get("default_implementation_class")
            logger.info(f"Class for AI_application {AI_application} is {impl_class}")
            if ai_application_name in self.cnf['AI_applications'] and "implementation_class" in self.cnf['AI_applications'][ai_application_name]:
                impl_class = self.cnf['AI_applications'][ai_application_name].get("implementation_class")
            if not impl_class:
                logger.error(f"Implementation class not found for AI_application {AI_application}")
                return
            impl_class = impl_class.strip()
            module_name, class_name = impl_class.strip().rsplit('.', 1)
            logger.info(f"Importing impl_class {impl_class}")
            module = importlib.import_module(module_name)
            logger.info(
                f"Getting class module_name={module_name} impl_class={impl_class} module={module} class_name={class_name}")
            class_ = getattr(module, class_name)
            logger.info(f"Got class {class_}")
            self.impl_map[ai_application_name] = class_(ai_application_name)
            if not llm_constants.paig_shield.DISABLE_PAIG_SHIELD_PLUGIN_FLAG:
                llm_constants.paig_shield.set_paig_config_map(ai_application_name,
                                                          self.cnf['AI_applications'][ai_application_name])

    def get_service(self, ai_application_name):
        service = self.impl_map.get(ai_application_name)
        if not service:
            logger.error(f"OpenAI Implementation Service not found for AI_application {ai_application_name}")
        return service
