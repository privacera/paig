from pydantic import BaseModel, Field


class InternalServerErrorFields(BaseModel):
    error_code: str = Field(default='500', validate_default=True)
    message: str = Field(default="Internal Server Error", validate_default=True)


class UnauthorizedErrorFields(BaseModel):
    error_code: str = Field(default='401', validate_default=True)
    message: str = Field(default="Unauthorized", validate_default=True)


class NotFoundErrorFields(BaseModel):
    error_code: str = Field(default='404', validate_default=True)
    message: str = Field(default="Not Found", validate_default=True)


CommonErrorResponse = {
    "500": {
        "model": InternalServerErrorFields
    },
    "401": {
        "model": UnauthorizedErrorFields
    },
    "404": {
        "model": NotFoundErrorFields
    }
}

InternalErrorResponse = {
    "500": {
        "model": InternalServerErrorFields
    }
}