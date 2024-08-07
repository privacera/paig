from presidio_analyzer import RecognizerResult


class AnalyzerResult(RecognizerResult):
    """
     AnalyzerResult extends RecognizerResult to include additional attributes such as model name and scanner name.
    """
    def __init__(self, start, end, entity_type, score, model_name, scanner_name, analysis_explanation,
                 recognition_metadata):
        """
            Initializes an instance of AnalyzerResult.
        """
        super().__init__(entity_type, start, end, score, analysis_explanation, recognition_metadata)
        self.model_name = model_name
        self.scanner_name = scanner_name

    def to_dict(self):
        """
        Converts the AnalyzerResult instance to a dictionary.

        Returns:
            dict: A dictionary representation of the AnalyzerResult instance.
        """
        return {
            'start': self.start,
            'end': self.end,
            'entity_type': self.entity_type,
            'score': self.score,
            'model_name': self.model_name,
            'scanner_name': self.scanner_name,
            'analysis_explanation': self.analysis_explanation,
            'recognition_metadata': self.recognition_metadata
        }
