from api.shield.scanners.ToxicContentScanner import ToxicContentScanner


class TestToxicContentScanner:

    def test_scan_non_toxic_text(self):
        toxic_scanner = ToxicContentScanner(name="toxic_content_scanner",
                                            request_types=['prompt', 'reply'],
                                            enforce_access_control=True,
                                            model_score_threshold=0.5,
                                            entity_type="TOXIC",
                                            enable=True)

        message = "What is LLM Guard library?"
        result = toxic_scanner.scan(message)

        assert result.get('traits') == []

    def test_scan_toxic_text(self):
        toxic_scanner = ToxicContentScanner(name="toxic_content_scanner",
                                            request_types=['prompt', 'reply'],
                                            enforce_access_control=True,
                                            model_score_threshold=0.5,
                                            entity_type="TOXIC",
                                            enable=True)

        message = "You are a stupid person"
        result = toxic_scanner.scan(message)

        assert result is not None
        assert result.get('traits') == ["TOXIC"]
        assert result.get('score') > 0.5
