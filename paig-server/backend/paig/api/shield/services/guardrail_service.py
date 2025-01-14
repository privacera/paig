import json


class GuardrailService:

    def process_guardrail_response(self, response:str):

        input_data = json.loads(response)
        result ={}

        for config in input_data.get("guardrail_configs", []):
            if "response_message" in config:
                result["response_message"] = config["response_message"]

            result["config_type"] = {}
            config_type = config["config_type"]
            result["config_type"][config_type] = {}
            for sub_config in config["config_data"]["configs"]:
                category = sub_config.get("category")
                action = sub_config.get("action", "DENY")
                if category and category not in result["config_type"][config_type]:
                    result["config_type"][config_type].update({category: action})

        return result

    def transform_guardrail_response(self, response:str):
        data = json.loads(response)

        # Initialize output structure
        result = {}

        # Process each guardrail
        for guardrail in data["guardrails"]:
            guardrail_provider_response = guardrail.get("guardrailProviderResponse", {})
            guardrail_connections = guardrail.get("guardrailConnections", {})

            for config in guardrail.get("guardrailConfigs", []):
                if config["guardrailProvider"] == "MULTIPLE":
                    for sub_config in config["configData"]["configs"]:
                        provider = sub_config["guardrailProvider"]

                        # Initialize provider structure if not exists
                        if provider not in result:
                            result[provider] = {"configType": {}}

                        # Add configType and categories
                        config_type = config["configType"]
                        if "responseMessage" in config:
                            result[provider]["responseMessage"] = config["responseMessage"]
                        if config_type not in result[provider]["configType"]:
                            result[provider]["configType"][config_type] = []

                        category = sub_config.get("category")
                        action = sub_config.get("action", "DENY")
                        if category and category not in result[provider]["configType"][config_type]:
                            result[provider]["configType"][config_type].append({category: action})

                        # Add guardrail details if present
                        provider_response = guardrail_provider_response.get(provider, {}).get("response", {})
                        for key in ["guardrailId", "version"]:
                            if key in provider_response:
                                result[provider][key] = provider_response[key]

                        # Add connection details if present
                        connection = guardrail_connections.get(provider, {})
                        for key in ["access_key", "secret_key", "session_token"]:
                            if key in connection:
                                result[provider][key] = connection[key]

                else:
                    provider = config["guardrailProvider"]

                    # Initialize provider structure if not exists
                    if provider not in result:
                        result[provider] = {"configType": {}}

                    # Add configType and categories
                    config_type = config["configType"]
                    if "responseMessage" in config:
                        result[provider]["responseMessage"] = config["responseMessage"]
                    if config_type not in result[provider]["configType"]:
                        result[provider]["configType"][config_type] = []

                    configs = config["configData"]["configs"]
                    for config in configs:
                        category = config.get("category", config.get("topic", config.get("term")))
                        action = config.get("action", "DENY")
                        if category and category not in result[provider]["configType"][config_type]:
                            result[provider]["configType"][config_type].append({category: action})

                    # Add guardrail details if present
                    provider_response = guardrail_provider_response.get(provider, {}).get("response", {})
                    for key in ["guardrailId", "version"]:
                        if key in provider_response:
                            result[provider][key] = provider_response[key]

                    # Add connection details if present
                    connection = guardrail_connections.get(provider, {})
                    for key in ["access_key", "secret_key", "session_token"]:
                        if key in connection:
                            result[provider][key] = connection[key]

    async def get_guardrail_by_id(self, request, tenant_id):
        guardrail_id = request.get("guardrailId")
        from api.shield.factory.guardrail_service_factory import GuardrailServiceFactory
        guardrail_service = GuardrailServiceFactory().get_guardrail_service_client()
        response = await guardrail_service.get_guardrail_info(tenant_id, guardrail_id)
        return response

    def test_guardrail(self, transformed_response:dict, message:str):

        from api.shield.scanners.PIIScanner import PIIScanner
        scanner = PIIScanner(name="PIIScanner", model_path="_")
        scanner_result = scanner.scan(message)

        deny_policies_list = []
        redact_policies_dict = {}
        # evaluate the guardrail PII policies
        sensitive_data_policies = transformed_response.get("config_type", {}).get("SENSITIVE_DATA", {})
        for key, value in sensitive_data_policies.items():
            if value == "DENY" and key in scanner_result.get_traits():
                deny_policies_list.append(key)
            elif value == "REDACT" and key in scanner_result.get_traits():
                redact_policies_dict.update({key: "<<"+key+">>"})

        if len(deny_policies_list) > 0:
            return {"action": "DENY", "message": f"PII policies violated: {deny_policies_list}"}

        if len(redact_policies_dict) > 0:
            # check the scanner_result for analyzer results
            # update the input text message with redacted values
            analyzer_results = scanner_result.get("analyzer_result")
            from api.shield.presidio.presidio_anonymizer_engine import PresidioAnonymizerEngine
            anonymizer = PresidioAnonymizerEngine()

            masked_text = anonymizer.mask(message, redact_policies_dict, analyzer_results)
            
            return {"action": "REDACT", "message": masked_text}

        return {"action": "ALLOW", "message": message}