from api.shield.presidio.presidio_anonymizer_engine import PresidioAnonymizerEngine
from presidio_analyzer import RecognizerResult


class TestPresidioAnonymizerEngine:

    def test_mask(self):
        text = "His name is Mr. Jones and his email is abc@xyz.com"
        masked_entities = {
            "PERSON": "<<PERSON>>",
            "EMAIL_ADDRESS": "<<EMAIL>>"
        }

        recognizer_result_1 = RecognizerResult("PERSON", 16, 21, 0.8)
        recognizer_result_2 = RecognizerResult("EMAIL_ADDRESS", 39, 50, 0.8)
        analyzer_result = [recognizer_result_1, recognizer_result_2]

        presidio_anonymizer = PresidioAnonymizerEngine()
        masked_text = presidio_anonymizer.mask(text, masked_entities, analyzer_result)

        assert masked_text == "His name is Mr. <<PERSON>> and his email is <<EMAIL>>"

    def test_anonymize(self):
        text = "His name is Mr. Jones and his email is abc@xyz.com"

        recognizer_result_1 = RecognizerResult("PERSON", 16, 21, 0.8)
        recognizer_result_2 = RecognizerResult("EMAIL_ADDRESS", 39, 50, 0.8)
        analyzer_result = [recognizer_result_1, recognizer_result_2]

        presidio_anonymizer = PresidioAnonymizerEngine()
        anonymized_text = presidio_anonymizer.anonymize(text, analyzer_result)

        assert anonymized_text == "His name is Mr. <PERSON> and his email is <EMAIL_ADDRESS>"
