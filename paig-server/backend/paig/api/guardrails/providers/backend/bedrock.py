from typing import List, Tuple

import boto3

from api.guardrails.providers import GuardrailProvider, GuardrailConfig
from api.guardrails.providers.models import GuardrailConfigType


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
        self.connection_details.setdefault('region', 'us-east-1')

    def verify_connection_details(self) -> Tuple[bool, str]:
        """
        Verify the necessary connection details and attempt to list guardrails.

        Returns:
            Tuple[bool, str]: A tuple containing a success flag and a friendly message.
                              If connection details are valid, returns True and a success message.
                              If invalid, returns False and a user-friendly error message.
        """
        if not self._has_valid_connection_keys():
            return False, "Connection details are incomplete. Please review your settings."

        try:
            client = self.create_bedrock_client()
            response = client.list_guardrails(maxResults=1)

            if response['ResponseMetadata']['HTTPStatusCode'] == 200:
                return True, "Connection successful!"
            else:
                return False, "We encountered an issue while verifying your settings. Please try again."

        except Exception as e:
            return False, "Unable to verify connection. Please check your details and try again."

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

    def create_guardrail(self, guardrail_configs: List[GuardrailConfig], **kwargs) -> Tuple[bool, dict]:
        """Create a guardrail using the provided configurations.

        Args:
            guardrail_configs (List[GuardrailConfig]): List of guardrail configurations.
            **kwargs: Additional keyword arguments.

        Returns:
            Tuple[bool, dict]: A tuple containing a success flag and the created guardrail details or error.
        """
        client = self.create_bedrock_client()
        payload = self.get_create_bedrock_guardrail_payload(guardrail_configs, **kwargs)

        return self._perform_guardrail_action(client.create_guardrail, payload)

    def update_guardrail(self, created_guardrail_details: dict, updated_guardrail_configs: List[GuardrailConfig],
                         **kwargs) -> Tuple[bool, dict]:
        """Update an existing guardrail with new configurations.

        Args:
            created_guardrail_details (dict): Details of the created guardrail.
            updated_guardrail_configs (List[GuardrailConfig]): Updated guardrail configurations.
            **kwargs: Additional keyword arguments.

        Returns:
            Tuple[bool, dict]: A tuple containing a success flag and the updated guardrail details or error.
        """
        client = self.create_bedrock_client()
        payload = self.get_create_bedrock_guardrail_payload(updated_guardrail_configs, **kwargs)
        payload['guardrailIdentifier'] = created_guardrail_details['response']['guardrailId']

        return self._perform_guardrail_action(client.update_guardrail, payload)

    def delete_guardrail(self, created_guardrail_details: dict, **kwargs) -> Tuple[bool, dict]:
        """Delete a specified guardrail.

        Args:
            created_guardrail_details (dict): Details of the guardrail to delete.
            **kwargs: Additional keyword arguments.

        Returns:
            Tuple[bool, dict]: A tuple containing a success flag and an empty dict or error.
        """
        client = self.create_bedrock_client()
        payload = {
            'guardrailIdentifier': created_guardrail_details['response']['guardrailId']
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

    def get_create_bedrock_guardrail_payload(self, guardrail_configs: List[GuardrailConfig], **kwargs) -> dict:
        """Construct the payload for creating a Bedrock guardrail.

        Args:
            guardrail_configs (List[GuardrailConfig]): List of guardrail configurations.
            **kwargs: Additional keyword arguments.

        Returns:
            dict: Payload for creating a Bedrock guardrail.
        """
        payload = {
            'name': kwargs.get('name'),
            'description': kwargs.get('description', ''),
            **{config.configType: config.configData for config in guardrail_configs}
        }

        # Set default messages if not provided
        payload.setdefault(GuardrailConfigType.BLOCKED_INPUTS_MESSAGING,
                           'Sorry, the model cannot answer this question.')
        payload.setdefault(GuardrailConfigType.BLOCKED_OUTPUTS_MESSAGING,
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
