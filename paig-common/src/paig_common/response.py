class Response:
    def __init__(self, content: str = "", status_code: int = 200):
        self.content = content
        self.status_code = status_code

    def to_flask_response(self):
        from flask import Response as FlaskResponse
        return FlaskResponse(response=self.content, status=self.status_code)

    def to_fastapi_response(self):
        from fastapi.responses import Response as FastApiResponse
        return FastApiResponse(content=self.content, status_code=self.status_code)

