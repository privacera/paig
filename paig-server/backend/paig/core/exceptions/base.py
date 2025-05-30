from http import HTTPStatus


class CustomException(Exception):
    code = HTTPStatus.BAD_GATEWAY
    error_code = HTTPStatus.BAD_GATEWAY
    message = HTTPStatus.BAD_GATEWAY.description
    details = None

    def __init__(self, message=None, details=None):
        if message:
            self.message = message
        if details:
            self.details = details

class TooManyRequestsException(CustomException):
    code = HTTPStatus.TOO_MANY_REQUESTS
    error_code = HTTPStatus.TOO_MANY_REQUESTS
    message = HTTPStatus.TOO_MANY_REQUESTS.description


class BadRequestException(CustomException):
    code = HTTPStatus.BAD_REQUEST
    error_code = HTTPStatus.BAD_REQUEST
    message = HTTPStatus.BAD_REQUEST.description


class NotFoundException(CustomException):
    code = HTTPStatus.NOT_FOUND
    error_code = HTTPStatus.NOT_FOUND
    message = HTTPStatus.NOT_FOUND.description


class ForbiddenException(CustomException):
    code = HTTPStatus.FORBIDDEN
    error_code = HTTPStatus.FORBIDDEN
    message = HTTPStatus.FORBIDDEN.description


class UnauthorizedException(CustomException):
    code = HTTPStatus.UNAUTHORIZED
    error_code = HTTPStatus.UNAUTHORIZED
    message = HTTPStatus.UNAUTHORIZED.description


class UnprocessableEntity(CustomException):
    code = HTTPStatus.UNPROCESSABLE_ENTITY
    error_code = HTTPStatus.UNPROCESSABLE_ENTITY
    message = HTTPStatus.UNPROCESSABLE_ENTITY.description


class InternalServerError(CustomException):
    code = HTTPStatus.INTERNAL_SERVER_ERROR
    error_code = HTTPStatus.INTERNAL_SERVER_ERROR
    message = HTTPStatus.INTERNAL_SERVER_ERROR.description


class ConflictException(CustomException):
    code = HTTPStatus.CONFLICT
    error_code = HTTPStatus.CONFLICT
    message = HTTPStatus.CONFLICT.description
