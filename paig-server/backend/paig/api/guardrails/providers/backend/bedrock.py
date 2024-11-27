import logging
from typing import Tuple, Dict

import boto3

from api.guardrails.providers import GuardrailProvider, UpdateGuardrailRequest, DeleteGuardrailRequest
from api.guardrails.providers.models import CreateGuardrailRequest, GuardrailRequest


logger = logging.getLogger(__name__)


class BedrockGuardrailConfigType:
    """Enumeration of guardrail configuration types."""
    TOPIC_POLICY_CONFIG = "topicPolicyConfig"
    CONTENT_POLICY_CONFIG = "contentPolicyConfig"
    WORD_POLICY_CONFIG = "wordPolicyConfig"
    SENSITIVE_INFORMATION_POLICY_CONFIG = "sensitiveInformationPolicyConfig"
    CONTEXTUAL_GROUNDING_POLICY_CONFIG = "contextualGroundingPolicyConfig"
    BLOCKED_INPUTS_MESSAGING = "blockedInputMessaging"
    BLOCKED_OUTPUTS_MESSAGING = "blockedOutputsMessaging"


class BedrockGuardrailProvider(GuardrailProvider):
    """Provider for managing Bedrock guardrails."""

    REQUIRED_ACCESS_KEYS = ['access_key', 'secret_key']
    REQUIRED_SESSION_KEYS = ['access_key', 'secret_key', 'session_token']
    REQUIRED_IAM_WEB_IDENTITY_KEYS = ['k8AwsRoleArn', 'k8AwsWebIdentityToken', 'sessionName']
    REQUIRED_IAM_ROLE_KEYS = ['iam_role']

    def __init__(self, connection_details: dict, **kwargs):
        """
        Initialize the BedrockGuardrailProvider.

        Args:
            connection_details (dict): Connection details for the provider.
            **kwargs: Additional keyword arguments.
        """
        super().__init__(connection_details, **kwargs)

        # Set default region if not provided
        self.connection_details.setdefault('region', 'us-east-1')

    def verify_connection_details(self) -> Tuple[bool, Dict]:
        """
        Verify the necessary connection details and attempt to list guardrails.

        Returns:
            Tuple[bool, Dict]: A tuple containing a success flag and a message or error details.
        """
        if not self._has_valid_connection_keys():
            return False, self._prepare_error_message_details("Connection details are incomplete. Please review your settings.")

        try:
            client = self.create_bedrock_client()
            response = client.list_guardrails(maxResults=1)

            if response['ResponseMetadata']['HTTPStatusCode'] == 200:
                return True, {"message": "Connection successful!"}
            else:
                return False, self._prepare_error_message_details("We encountered an issue while verifying your settings. Please try again.")

        except Exception as e:
            return False, self._prepare_error_message_details("Unable to verify connection. Please check your details and try again.")

    def _prepare_error_message_details(self, message: str) -> Dict:
        """
        Prepare error message details from passed message.

        Args:
            message (str): The error message.

        Returns:
            Dict: A dictionary containing the error message details.
        """
        return {
            "error": message
        }

    def _has_valid_connection_keys(self) -> bool:
        """
        Check if any of the valid key sets are present in the connection details.

        Returns:
            bool: True if a valid set of connection keys is present, False otherwise.
        """
        return any(
            all(key in self.connection_details for key in keys)
            for keys in (self.REQUIRED_SESSION_KEYS, self.REQUIRED_ACCESS_KEYS, self.REQUIRED_IAM_WEB_IDENTITY_KEYS, self.REQUIRED_IAM_ROLE_KEYS)
        )

    def create_guardrail(self, request: CreateGuardrailRequest, **kwargs) -> Tuple[bool, dict]:
        """Create a guardrail using the provided configurations.

        Args:
            request (CreateGuardrailRequest): The request containing guardrail configurations.
            **kwargs: Additional keyword arguments.

        Returns:
            Tuple[bool, dict]: A tuple containing a success flag and the created guardrail details or error.
        """
        client = self.create_bedrock_client()
        payload = self.get_create_bedrock_guardrail_payload(request, **kwargs)

        return self._perform_guardrail_action(client.create_guardrail, payload)

    def update_guardrail(self, request: UpdateGuardrailRequest, **kwargs) -> Tuple[bool, dict]:
        """Update an existing guardrail with new configurations.

        Args:
            request (UpdateGuardrailRequest): A request object containing updated guardrail configurations.
            **kwargs: Additional keyword arguments.

        Returns:
            Tuple[bool, dict]: A tuple containing a success flag and the updated guardrail details or error.
        """
        client = self.create_bedrock_client()
        payload = self.get_create_bedrock_guardrail_payload(request, **kwargs)

        if not request.remoteGuardrailDetails['success']:
            logger.warning("Guardrail not found. Running create instead of update for guardrail %s of bedrock.", request.name)
            return self._perform_guardrail_action(client.create_guardrail, payload)

        payload['guardrailIdentifier'] = request.remoteGuardrailDetails['response']['guardrailId']
        return self._perform_guardrail_action(client.update_guardrail, payload)

    def delete_guardrail(self, request: DeleteGuardrailRequest, **kwargs) -> Tuple[bool, dict]:
        """Delete a specified guardrail.

        Args:
            request (DeleteGuardrailRequest): A request object containing guardrail details.
            **kwargs: Additional keyword arguments.

        Returns:
            Tuple[bool, dict]: A tuple containing a success flag and an empty dict or error.
        """
        client = self.create_bedrock_client()

        if request.remoteGuardrailDetails['success'] is False:
            logger.warning("Guardrail not found. Skipping deletion for guardrail %s of bedrock.", request.name)
            return True, {}

        payload = {
            'guardrailIdentifier': request.remoteGuardrailDetails['response']['guardrailId']
        }

        return self._perform_guardrail_action(client.delete_guardrail, payload)

    def create_bedrock_client(self):
        """Create a Boto3 client for the Bedrock service based on the provided credentials.

        Returns:
            boto3.client: A Boto3 client for the Bedrock service.
        """
        if all(key in self.connection_details for key in self.REQUIRED_SESSION_KEYS):
            return boto3.client(
                'bedrock',
                aws_access_key_id=self.connection_details['access_key'],
                aws_secret_access_key=self.connection_details['secret_key'],
                aws_session_token=self.connection_details['session_token'],
                region_name=self.connection_details['region']
            )

        if all(key in self.connection_details for key in self.REQUIRED_ACCESS_KEYS):
            return boto3.client(
                'bedrock',
                aws_access_key_id=self.connection_details['access_key'],
                aws_secret_access_key=self.connection_details['secret_key'],
                region_name=self.connection_details['region']
            )

        if all(key in self.connection_details for key in self.REQUIRED_IAM_WEB_IDENTITY_KEYS):
            sts_client = boto3.client('sts')
            assumed_role = sts_client.assume_role_with_web_identity(
                RoleArn=self.connection_details['k8AwsRoleArn'],
                RoleSessionName=self.connection_details['sessionName'],
                WebIdentityToken=self.connection_details['k8AwsWebIdentityToken']
            )
            temp_credentials = assumed_role['Credentials']
            return boto3.client(
                'bedrock',
                aws_access_key_id=temp_credentials['AccessKeyId'],
                aws_secret_access_key=temp_credentials['SecretAccessKey'],
                aws_session_token=temp_credentials['SessionToken'],
                region_name=self.connection_details['region']
            )

        return boto3.client('bedrock', region_name=self.connection_details['region'])

    def get_create_bedrock_guardrail_payload(self, request: GuardrailRequest, **kwargs) -> dict:
        """Construct the payload for creating a Bedrock guardrail.

        Args:
            request (CreateGuardrailRequest): The request containing guardrail configurations.
            **kwargs: Additional keyword arguments.

        Returns:
            dict: Payload for creating a Bedrock guardrail.
        """
        payload = {
            'name': request.name,
            'description': request.description,
            **{config.configType: config.configData for config in request.guardrailConfigs}
        }

        # Set default messages if not provided
        payload.setdefault(BedrockGuardrailConfigType.BLOCKED_INPUTS_MESSAGING,
                           'Sorry, the model cannot answer this question.')
        payload.setdefault(BedrockGuardrailConfigType.BLOCKED_OUTPUTS_MESSAGING,
                           'Sorry, the model cannot answer this question.')

        # Add optional fields to the payload
        if kms_key_id := kwargs.get('kmsKeyId'):
            payload['kmsKeyId'] = kms_key_id

        if tags := kwargs.get('tags'):
            payload['tags'] = tags

        return payload

    def _perform_guardrail_action(self, action_func, payload: dict) -> Tuple[bool, dict]:
        """Perform a guardrail action (create/update/delete) and handle exceptions.

        Args:
            action_func (callable): The action function to call (create/update/delete).
            payload (dict): The payload for the action.

        Returns:
            Tuple[bool, dict]: A tuple containing a success flag and the result or error.
        """
        try:
            response = action_func(**payload)
            return True, self._extract_guardrail_details(response)
        except Exception as e:
            return False, self.handle_bedrock_exceptions(e, self.create_bedrock_client())

    def _extract_guardrail_details(self, response: dict) -> dict:
        """Extract relevant guardrail details from the response.

        Args:
            response (dict): The response from the Bedrock service.

        Returns:
            dict: A dictionary containing guardrail details.
        """
        details = {}

        if 'guardrailId' in response:
            details['guardrailId'] = response['guardrailId']
        if 'guardrailArn' in response:
            details['guardrailArn'] = response['guardrailArn']
        if 'version' in response:
            details['version'] = response['version']

        return details

    def handle_bedrock_exceptions(self, e, client) -> dict:
        """Handle Bedrock client exceptions and return appropriate error messages and details.

        Args:
            e (Exception): The caught exception.
            client: The Bedrock client instance.

        Returns:
            dict: A dictionary containing error messages and details.
        """
        exception_mapping = {
            client.exceptions.ResourceNotFoundException: "Resource not found. Please verify that the resource you are trying to access exists.",
            client.exceptions.AccessDeniedException: "Access denied. Please ensure you have the correct permissions.",
            client.exceptions.ValidationException: "Validation error. Please check the provided configuration and ensure all fields are valid.",
            client.exceptions.ConflictException: "Conflict error. The resource already exists or there is a conflict with the request.",
            client.exceptions.InternalServerException: "Internal server error. Please try again later.",
            client.exceptions.ServiceQuotaExceededException: "Service quota exceeded. Please review your usage limits and adjust accordingly.",
            client.exceptions.ThrottlingException: "Request throttled. Too many requests have been made. Please try again after some time."
        }

        error_type = type(e)
        return {
            "message": exception_mapping.get(error_type, "An unknown error occurred. Please contact support."),
            "details": {"errorType": error_type.__name__, "details": str(e)}
        }
