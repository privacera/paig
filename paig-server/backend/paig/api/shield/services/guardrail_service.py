import json
import logging

logger = logging.getLogger(__name__)

def process_guardrail_response(input_data: dict):

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

def transform_guardrail_response(input_data: dict):

    result = []

    # Process each guardrail
    for guardrail in input_data["guardrails"]:
        result.append(process_guardrail_response(guardrail))

    return result

async def get_guardrail_by_id(request, tenant_id):
    guardrail_id = request.get("guardrailId")
    from api.shield.factory.guardrail_service_factory import GuardrailServiceFactory
    guardrail_service = GuardrailServiceFactory().get_guardrail_service_client()
    response = await guardrail_service.get_guardrail_info(tenant_id, guardrail_id)
    return response


async def decrypted_connection_details(connection_details: dict):
    from api.encryption.services.encryption_key_service import EncryptionKeyService
    from api.encryption.api_schemas.encryption_key import EncryptionKeyView
    from api.shield.utils.custom_exceptions import BadRequestException

    encryption_service = EncryptionKeyService()
    encryption_key_info: EncryptionKeyView = await encryption_service.get_encryption_key_by_id(connection_details.get("encryption_key_id"))

    from paig_common.encryption import DataEncryptor
    data_encryptor = DataEncryptor(public_key=encryption_key_info.public_key, private_key=encryption_key_info.private_key)
    for key, value in connection_details.items():
        connection_details_value = str(value)
        if connection_details_value.startswith("GuardrailEncrypt:"):
            try:
                connection_details[key] = data_encryptor.decrypt(data=connection_details_value.replace("GuardrailEncrypt:", ""))
            except Exception as e:
                raise BadRequestException(
                    f"Invalid connection details('{key}') for {connection_details_value}. Got error {e}")

async def test_guardrail(transformed_response:dict, message:str):

    final_result = [test_paig_guardrail(transformed_response, message)]
    if isinstance(final_result[0], dict) and "DENY" not in final_result[0].get("action", ""):
        test_aws_guardrail_result = await test_aws_guardrail(transformed_response, message)
        if test_aws_guardrail_result:
            final_result.append(test_aws_guardrail_result)

    for result in final_result:
        if result.get("action") == "DENY":
            return result
    return final_result

def paig_pii_guardrail_evaluation(sensitive_data_config:dict, traits:list) -> (list, dict):
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

def mask_message(message:str, redact_policies_dict:dict, analyzer_results: list) -> str:
    # check the scanner_result for analyzer results
    # update the input text message with redacted values
    custom_mask_analyzer_result = [x for x in analyzer_results if
                                   x.entity_type in redact_policies_dict.keys()]
    from api.shield.presidio.presidio_anonymizer_engine import PresidioAnonymizerEngine
    anonymizer = PresidioAnonymizerEngine()
    masked_message = anonymizer.mask(message, redact_policies_dict, custom_mask_analyzer_result)

    return masked_message

def test_paig_guardrail(transformed_response:dict, message:str) -> dict:
    from api.shield.scanners.PIIScanner import PIIScanner
    scanner = PIIScanner(name="PIIScanner", model_path="_")
    scanner_result = scanner.scan(message)

    sensitive_data_config = transformed_response.get("config_type", {}).get("SENSITIVE_DATA", {})
    deny_policies_list, redact_policies_dict = paig_pii_guardrail_evaluation(sensitive_data_config, scanner_result.get_traits())

    if len(deny_policies_list) > 0:
        return {"action": "DENY", "tags": scanner_result.get_traits(), "policy": ["SENSITIVE_DATA"], "message": f'{sensitive_data_config.get("response_message")}'}

    if len(redact_policies_dict) > 0:
        masked_message = mask_message(message, redact_policies_dict, scanner_result.get("analyzer_result", []))
        return {"action": "REDACT", "tags": scanner_result.get_traits(), "policy": ["SENSITIVE_DATA"], "message": masked_message}

    return {"action": "ALLOW", "tags": scanner_result.get_traits(), "policy": ["SENSITIVE_DATA"], "message": message}

async def test_aws_guardrail(transformed_response:dict, message:str) -> None|dict:

    # check if AWS guardrail is present
    guardrail_provider_details = transformed_response.get("guardrail_provider_details", {})
    if not "AWS" in guardrail_provider_details:
        logger.debug("AWS Guardrail not configured. Hence skipping the AWS Guardrail test.")
        return {}

    aws_guardrail_details = guardrail_provider_details.get("AWS", {})
    import api.shield.scanners.AWSBedrockGuardrailScanner as awsGuardrailScanner
    aws_guardrail_id = aws_guardrail_details.get("guardrailId")
    aws_guardrail_version = aws_guardrail_details.get("version")
    aws_guardrail_region = "us-east-1"

    aws_guardrail_connection_details = aws_guardrail_details.get("connection_details", {})
    if aws_guardrail_connection_details:
        await decrypted_connection_details(aws_guardrail_connection_details)
        aws_guardrail_region = aws_guardrail_connection_details.get("region", "us-east-1")

    aws_guardrail_scanner_instance = awsGuardrailScanner.AWSBedrockGuardrailScanner(guardrail_id=aws_guardrail_id,
                                                                                      guardrail_version=aws_guardrail_version,
                                                                                      region=aws_guardrail_region,
                                                                                      connection_details=aws_guardrail_connection_details)
    scanner_result = aws_guardrail_scanner_instance.scan(message)
    if scanner_result.get("actions"):
        policies_identified = []
        response_msg = scanner_result.get("output_text")
        for key, value in transformed_response.get("config_type", {}).items():
            for category, action in value.get("configs", {}).items():
                if category.upper() in scanner_result.get_traits():
                    response_msg = value.get("response_message")
                    policies_identified.append(key)
        return {"action": "DENY", "tags": scanner_result.get_traits(), "policy": policies_identified, "message": response_msg }
