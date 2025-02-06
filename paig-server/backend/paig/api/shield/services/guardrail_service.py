import json
import logging

logger = logging.getLogger(__name__)

def process_guardrail_response(response: str):
    input_data = json.loads(response)

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
            category = sub_config.get("category") or sub_config.get("type") or sub_config.get("term")
            action = sub_config.get("action", "DENY") or sub_config.get("value")
            if category:
                result["config_type"][config_type]["configs"][category] = action

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


def transform_guardrail_response(response:str):
    data = json.loads(response)

    # Initialize output structure
    result = {}

    # Process each guardrail
    for guardrail in data["guardrails"]:
        guardrail_provider_response = guardrail.get("guardrailProviderResponse", {})
        guardrail_connections = guardrail.get("guardrailConnections", {})

        for guardrail_config in guardrail.get("guardrailConfigs", []):
            if guardrail_config["guardrailProvider"] == "MULTIPLE":
                for sub_config in guardrail_config["configData"]["configs"]:
                    provider = sub_config["guardrailProvider"]

                    # Initialize provider structure if not exists
                    if provider not in result:
                        result[provider] = {"configType": {}}

                    # Add configType and categories
                    config_type = guardrail_config["configType"]
                    if "responseMessage" in guardrail_config:
                        result[provider]["responseMessage"] = guardrail_config["responseMessage"]
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
                provider = guardrail_config["guardrailProvider"]

                # Initialize provider structure if not exists
                if provider not in result:
                    result[provider] = {"configType": {}}

                # Add configType and categories
                config_type = guardrail_config["configType"]
                if "responseMessage" in guardrail_config:
                    result[provider]["responseMessage"] = guardrail_config["responseMessage"]
                if config_type not in result[provider]["configType"]:
                    result[provider]["configType"][config_type] = []

                configs = guardrail_config["configData"]["configs"]
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


async def get_guardrail_by_id(request, tenant_id):
    guardrail_id = request.get("guardrailId")
    from api.shield.factory.guardrail_service_factory import GuardrailServiceFactory
    guardrail_service = GuardrailServiceFactory().get_guardrail_service_client()
    response = await guardrail_service.get_guardrail_info(tenant_id, guardrail_id)
    return response



def test_guardrail(transformed_response:dict, message:str):

    final_result = {}
    final_result.update(test_paig_guardrail(transformed_response, message))
    final_result.update(test_aws_guardrail(transformed_response, message))
    return final_result

def test_paig_guardrail(transformed_response:dict, message:str) -> dict:
    from api.shield.scanners.PIIScanner import PIIScanner
    scanner = PIIScanner(name="PIIScanner", model_path="_")
    scanner_result = scanner.scan(message)

    deny_policies_list = []
    redact_policies_dict = {}
    # evaluate the guardrail PII policies
    sensitive_data_policies = transformed_response.get("config_type", {}).get("SENSITIVE_DATA", {}).get("configs", {})
    for key, value in sensitive_data_policies.items():
        if value == "DENY" and key in scanner_result.get_traits():
            deny_policies_list.append(key)
        elif value == "REDACT" and key in scanner_result.get_traits():
            redact_policies_dict.update({key: "<<"+key+">>"})

    if len(deny_policies_list) > 0:
        return {"action": "DENY", "message": f'{transformed_response.get("config_type", {}).get("SENSITIVE_DATA", {}).get("response_message")}'}

    if len(redact_policies_dict) > 0:
        # check the scanner_result for analyzer results
        # update the input text message with redacted values
        analyzer_results = scanner_result.get("analyzer_result")
        custom_mask_analyzer_result = [x for x in analyzer_results if
                                       x.entity_type in redact_policies_dict.keys()]
        from api.shield.presidio.presidio_anonymizer_engine import PresidioAnonymizerEngine
        anonymizer = PresidioAnonymizerEngine()
        masked_text = anonymizer.mask(message, redact_policies_dict, custom_mask_analyzer_result)

        return {"action": "REDACT", "message": masked_text}

    return {"action": "ALLOW", "message": message}

def test_aws_guardrail(transformed_response:dict, message:str) -> dict:

    # check if AWS guardrail is present
    guardrail_provider_details = transformed_response.get("guardrail_provider_details", {})
    if not "AWS" in guardrail_provider_details:
        logger.debug("AWS Guardrail not configured. Hence skipping the AWS Guardrail test.")
        return {}

    aws_guardrail_details = guardrail_provider_details.get("AWS", {})
    import api.shield.scanners.AWSBedrockGuardrailScanner as aws_guardrail_scanner
    aws_guardrail_id = aws_guardrail_details.get("guardrailId")
    aws_guardrail_version = aws_guardrail_details.get("version")
    aws_guardrail_region = "us-east-1"

    aws_guardrail_connection_details = aws_guardrail_details.get("connection_details", {})
    if aws_guardrail_connection_details:
        aws_guardrail_region = aws_guardrail_connection_details.get("region", "us-east-1")

    aws_guardrail_scanner_instance = aws_guardrail_scanner.AWSBedrockGuardrailScanner(guardrail_id=aws_guardrail_id,
                                                                                      guardrail_version=aws_guardrail_version,
                                                                                      region=aws_guardrail_region,
                                                                                      connection_details=aws_guardrail_connection_details)
    scanner_result = aws_guardrail_scanner_instance.scan(message)
    if scanner_result.get("actions"):
        #TODO: get response message based on policy identified from the guardrail
        return {"action": "DENY", "Policy": scanner_result.get_traits(), "message": f'{aws_guardrail_scanner_instance.get_property("response_message")}'}
    else:
        return {}
