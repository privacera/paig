from datetime import datetime, timedelta

from jose import ExpiredSignatureError, JWTError, jwt

from core.config import load_config_file
from core.exceptions import CustomException

Config = load_config_file()
DEFAULT_SECRET_KEY = "s67e5f1d7a1be73b26316bcfbac0faa06f2b984e259824bc2f96f12f8c3943408"


class JWTDecodeError(CustomException):
    code = 401
    message = "Invalid token"


class JWTExpiredError(CustomException):
    code = 401
    message = "Token expired"


class JWTHandler:
    security_conf = Config['security']
    secret_key = security_conf.get('secret_key', DEFAULT_SECRET_KEY)
    algorithm = security_conf.get('algorithm', "HS256")
    expire_minutes = security_conf.get('expire_minutes', 60)

    @staticmethod
    def encode(payload: dict) -> str:
        expire = datetime.utcnow() + timedelta(minutes=JWTHandler.expire_minutes)
        payload.update({"exp": expire})
        return jwt.encode(
            payload, JWTHandler.secret_key, algorithm=JWTHandler.algorithm
        )

    @staticmethod
    def decode(token: str) -> dict:
        try:
            return jwt.decode(
                token, JWTHandler.secret_key, algorithms=[JWTHandler.algorithm]
            )
        except ExpiredSignatureError as exception:
            raise JWTExpiredError() from exception
        except JWTError as exception:
            raise JWTDecodeError() from exception

    @staticmethod
    def decode_expired(token: str) -> dict:
        try:
            return jwt.decode(
                token,
                JWTHandler.secret_key,
                algorithms=[JWTHandler.algorithm],
                options={"verify_exp": False},
            )
        except JWTError as exception:
            raise JWTDecodeError() from exception