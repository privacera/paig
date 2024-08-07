from core.security.jwt import JWTHandler
import pytest


class TestJWTHandler:
    @pytest.fixture
    def jwt_handler(self):
        return JWTHandler()

    def test_create_jwt_token(self, jwt_handler):
        token = jwt_handler.encode({"user": "test"})
        assert token is not None

    def test_decode_jwt_token(self, jwt_handler):
        token = jwt_handler.encode({"user": "test"})
        token = jwt_handler.decode(token)
        assert token['user'] == "test"

    def test_decode_jwt_token_with_invalid_token(self, jwt_handler):
        with pytest.raises(Exception) as e:
            jwt_handler.decode("invalid_token")
        assert str(e.value) != None
