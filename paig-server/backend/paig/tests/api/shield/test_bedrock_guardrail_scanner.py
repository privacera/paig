from api.shield.scanners.BedrockGuardrailScanner import BedrockGuardrailScanner

import pytest
import os

class TestBedrockGuardrailScanner:

    # Initialize BedrockGuardrailScanner with valid parameters and verify attributes are set correctly
    def test_initialize_with_valid_parameters(self, mocker):
        mocker.patch('boto3.client')
        scanner = BedrockGuardrailScanner(name='TestScanner', request_types=['type1'], enforce_access_control=True, model_path='/path/to/model', model_score_threshold=0.5, entity_type='entity', enable=True, guardrail_id='guardrail_id', guardrail_version='guardrail_version', region='us-west-2')
        assert scanner.guardrail_id is not None
        assert scanner.guardrail_version is not None
        assert scanner.region is not None

    # Scan a message that triggers guardrail intervention and verify correct ScannerResult
    def test_scan_triggers_guardrail_intervention(self, mocker):
        mock_bedrock_client = mocker.patch('boto3.client')
        mock_bedrock_client.return_value.apply_guardrail.return_value = {
            'action': 'GUARDRAIL_INTERVENED',
            'outputs': [{'text': 'Intervened text'}],
            'assessments': [{'policy1': {'data1': [{'type': 'TAG1', 'action': 'ACTION1'}]}}]
        }
        scanner = BedrockGuardrailScanner(guardrail_id='guardrail_id', guardrail_version='guardrail_version', region='us-west-2')
        result = scanner.scan('trigger message')
        assert result.traits == ['TAG1']
        assert result.actions == ['ACTION1']
        assert result.output_text == 'Intervened text'

    # Scan a message that triggers guardrail intervention and verify ScannerResult contains expected traits and actions
    def test_scan_with_guardrail_intervention(self, mocker):
        mock_bedrock_client = mocker.patch('boto3.client')
        mock_bedrock_client.return_value.apply_guardrail.return_value = {
            'action': 'GUARDRAIL_INTERVENED',
            'outputs': [{'text': 'Intervened text'}],
            'assessments': [{'policy1': {'data1': [{'type': 'type1', 'action': 'action1'}]}}]
        }
        scanner = BedrockGuardrailScanner(name='TestScanner', guardrail_id='guardrail_id', guardrail_version='guardrail_version', region='us-west-2')
        result = scanner.scan('trigger message')
        assert result.traits == ['TYPE1']
        assert result.actions == ['action1']
        assert result.output_text == 'Intervened text'

    # Scan a message that does not trigger intervention and verify empty traits in ScannerResult
    def test_scan_no_intervention(self, mocker):
        mock_bedrock_client = mocker.patch('boto3.client')
        mock_bedrock_client.return_value.apply_guardrail.return_value = {'action': 'NO_ACTION'}
        scanner = BedrockGuardrailScanner(guardrail_id='guardrail_id', guardrail_version='guardrail_version', region='us-west-2')
        result = scanner.scan('non-trigger message')
        assert result.traits == []

    # Scan a message that does not trigger guardrail intervention and verify ScannerResult has empty traits
    def test_scan_without_guardrail_intervention(self, mocker):
        mock_bedrock_client = mocker.patch('boto3.client')
        mock_bedrock_client.return_value.apply_guardrail.return_value = {'action': 'NO_ACTION'}
        scanner = BedrockGuardrailScanner(name='TestScanner', guardrail_id='guardrail_id', guardrail_version='guardrail_version', region='us-west-2')
        result = scanner.scan('non-trigger message')
        assert result.traits == []

    # Initialize BedrockGuardrailScanner with missing mandatory parameters and expect an error
    def test_initialize_with_missing_parameters(self):
        with pytest.raises(ValueError):
            BedrockGuardrailScanner()

    # Handle missing guardrail ID, version, or region gracefully and raise appropriate errors
    def test_missing_guardrail_details_raises_error(self, mocker):
        mocker.patch('os.environ.get', return_value=None)
        with pytest.raises(ValueError, match="Bedrock Guardrail ID not found in properties or environment variables."):
            BedrockGuardrailScanner()

    # Scan a message with an empty string and verify ScannerResult is handled correctly
    def test_scan_with_empty_message(self, mocker):
        mock_bedrock_client = mocker.patch('boto3.client')
        mock_bedrock_client.return_value.apply_guardrail.return_value = {'action': 'NO_ACTION'}
        scanner = BedrockGuardrailScanner(name='TestScanner', guardrail_id='guardrail_id', guardrail_version='guardrail_version', region='us-west-2')
        result = scanner.scan('')
        assert result.traits == []

    # Scan an empty message and verify correct handling without errors
    def test_scan_empty_message(self, mocker):
        mock_bedrock_client = mocker.patch('boto3.client')
        mock_bedrock_client.return_value.apply_guardrail.return_value = {'action': 'NO_ACTION'}
        scanner = BedrockGuardrailScanner(guardrail_id='guardrail_id', guardrail_version='guardrail_version', region='us-west-2')
        result = scanner.scan('')
        assert result.traits == []

    # Handle missing or malformed assessment data gracefully in _extract_and_populate_assessment_info
    def test_extract_and_populate_assessment_info_with_malformed_data(self):
        scanner = BedrockGuardrailScanner(name='TestScanner', guardrail_id='guardrail_id', guardrail_version='guardrail_version', region='us-west-2')
        tag_set, action_set = scanner._extract_and_populate_assessment_info([{'policy1': {}}])
        assert tag_set == set()
        assert action_set == set()

    # Handle response with no outputs gracefully in scan method
    def test_scan_no_outputs_in_response(self, mocker):
        mock_bedrock_client = mocker.patch('boto3.client')
        mock_bedrock_client.return_value.apply_guardrail.return_value = {
            'action': 'GUARDRAIL_INTERVENED',
            'outputs': [],
            'assessments': [{'policy1': {'data1': [{'type': 'TAG1', 'action': 'ACTION1'}]}}]
        }
        scanner = BedrockGuardrailScanner(guardrail_id='guardrail_id', guardrail_version='guardrail_version', region='us-west-2')
        result = scanner.scan('trigger message')
        assert result.output_text is None

    # Test behavior when environment variables for guardrail details are not set
    def test_guardrail_details_without_env_variables(self, mocker):
        mocker.patch.dict(os.environ, {}, clear=True)
        with pytest.raises(ValueError):
            BedrockGuardrailScanner(name='TestScanner')

    # Handle response with no assessments gracefully in scan method
    def test_scan_no_assessments_in_response(self, mocker):
        mock_bedrock_client = mocker.patch('boto3.client')
        mock_bedrock_client.return_value.apply_guardrail.return_value = {
            'action': 'GUARDRAIL_INTERVENED',
            'outputs': [{'text': 'Intervened text'}],
            'assessments': []
        }
        scanner = BedrockGuardrailScanner(guardrail_id='guardrail_id', guardrail_version='guardrail_version', region='us-west-2')
        result = scanner.scan('trigger message')
        assert result.traits == []
        assert result.actions == []