from api.shield.presidio.presidio_analyzer_engine import PresidioAnalyzerEngine


class TestPresidioAnalyzerEngine:

    def test_analyze_text(self, mocker):
        side_effect = lambda prop: {
            "presidio_analyzer_score_threshold": 0.6,
        }.get(prop)
        mocker.patch('api.shield.utils.config_utils.get_property_value_float', side_effect=side_effect)

        presidio_analyzer_engine = PresidioAnalyzerEngine()
        text = "His name is Mr. Jones and his email is abc@xyz.com"

        result = presidio_analyzer_engine.analyze(text)

        assert result is not None
        assert len(result) == 2
        assert result[0].entity_type == "EMAIL_ADDRESS"
        assert result[1].entity_type == "PERSON"

    def test_remove_recognizers(self, mocker):
        side_effect = lambda prop: {
            "presidio_analyzer_score_threshold": 0.6,
        }.get(prop)
        mocker.patch('api.shield.utils.config_utils.get_property_value_float', side_effect=side_effect)

        # mocking this to remove a recognizer which is not default for presidio
        side_effect = lambda prop, default_value=None: {
            "presidio_recognizers_to_remove": "EmailRecognizer_NA",
        }.get(prop, default_value)
        mocker.patch('api.shield.utils.config_utils.get_property_value', side_effect=side_effect)

        presidio_analyzer_engine = PresidioAnalyzerEngine()
        text = "His name is Mr. Jones and his email is abc@xyz.com"

        recognizer_list_before = presidio_analyzer_engine.analyzer.registry.recognizers
        assert len(recognizer_list_before) == 23

        result = presidio_analyzer_engine.analyze(text)

        assert result is not None
        assert len(result) == 2
        assert result[0].entity_type == "EMAIL_ADDRESS"
        assert result[1].entity_type == "PERSON"

        # mock the recognizers to remove to EmailRecognizer
        side_effect = lambda prop, default_value=None: {
            "presidio_recognizers_to_remove": "EmailRecognizer",
        }.get(prop, default_value)
        mocker.patch('api.shield.utils.config_utils.get_property_value', side_effect=side_effect)

        presidio_analyzer_engine.remove_unwanted_recognizers()
        recognizer_list_after = presidio_analyzer_engine.analyzer.registry.recognizers

        # check if the recognizer is removed
        assert len(recognizer_list_after) == 22

        result = presidio_analyzer_engine.analyze(text)

        # verify the result after removing the recognizer, the email address should not be detected
        assert result is not None
        assert len(result) == 1
        assert result[0].entity_type != "EMAIL_ADDRESS"
        assert result[0].entity_type == "PERSON"
