from api.shield.scanners.ToxicContentScanner import ToxicContentScanner


class TestToxicContentScanner:

    def test_scan_non_toxic_text(self):

        _name = "toxic_content_scanner"
        _request_types = ['prompt', 'reply']
        _enforce_access_control = False
        _model_path = "test/prompt_injection_model"
        _model_score_threshold = 0.5
        _entity_type = "TOXIC"
        _enable = True

        toxic_scanner = ToxicContentScanner(_name, _request_types, _enforce_access_control, _model_path,
                                            _model_score_threshold, _entity_type, _enable)

        message = "What is LLM Guard library?"
        result = toxic_scanner.scan(message)

        assert result == {}

    def test_scan_toxic_text(self):

        _name = "toxic_content_scanner"
        _request_types = ['prompt', 'reply']
        _enforce_access_control = False
        _model_path = "test/prompt_injection_model"
        _model_score_threshold = 0.5
        _entity_type = "TOXIC"
        _enable = True

        toxic_scanner = ToxicContentScanner(_name, _request_types, _enforce_access_control, _model_path,
                                            _model_score_threshold, _entity_type, _enable)

        message = "You are a stupid person"
        result = toxic_scanner.scan(message)

        assert result != {}
        assert result["traits"] == ["TOXIC"]
        assert result["score"] > _model_score_threshold
