from pydantic import BaseModel, Field


class InternalServerModel(BaseModel):
    error_code: str = Field(default='500', validate_default=True)
    message: str = Field(default="Internal Server Error", validate_default=True)


class UnauthorizedModel(BaseModel):
    error_code: str = Field(default='401', validate_default=True)
    message: str = Field(default="Unauthorized", validate_default=True)


class NotFoundModel(BaseModel):
    error_code: str = Field(default='404', validate_default=True)
    message: str = Field(default="Not Found", validate_default=True)


class BadRequestModel(BaseModel):
    error_code: str = Field(default='400', validate_default=True)
    message: str = Field(default="Bad Request", validate_default=True)


CommonErrorResponse = {
    "500": {
        "model": InternalServerModel
    },
    "401": {
        "model": UnauthorizedModel
    },
    "404": {
        "model": NotFoundModel
    },
    "400": {
        "model": BadRequestModel
    }
}

InternalErrorResponse = {
    "500": {
        "model": InternalServerModel
    }
}