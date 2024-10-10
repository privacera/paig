import pytest
from unittest.mock import patch
from core.security.authentication import get_auth_user, UnauthorizedException
from core.security.okta_verifier import PaigOktaVerifier

class MockRequest:
    def __init__(self, cookies):
        self.cookies = cookies

class MockUserController:
    async def get_user(self, user):
        return {"user_id": 1, "user_name": "test_user"}

class TestGetAuthUser:
    @pytest.mark.asyncio
    async def test_valid_session(self):
        mock_user = {"user_id": 1, "user_name": "test_user"}
        mock_session_token = "valid_session_token"
        mock_request = MockRequest(cookies={"session": mock_session_token})
        mock_user_controller = MockUserController()

        def mock_decode(token):
            return mock_user

        with patch('core.security.authentication.jwt_handler.decode', new=mock_decode):
            result = await get_auth_user(mock_request, mock_user_controller)

        assert result == mock_user

    @pytest.mark.asyncio
    async def test_invalid_session(self):
        mock_request = MockRequest(cookies={})
        mock_user_controller = MockUserController()

        def mock_decode(token):
            return None

        with patch('core.security.authentication.jwt_handler.decode', new=mock_decode):
            with pytest.raises(UnauthorizedException, match="Unauthorized session"):
                await get_auth_user(mock_request, mock_user_controller)

    @pytest.mark.asyncio
    async def test_unauthorized_user(self):
        mock_user = {"user_id": 1, "user_name": "test_user"}
        mock_session_token = "valid_session_token"
        mock_request = MockRequest(cookies={"session": mock_session_token})
        mock_user_controller = MockUserController()

        def mock_decode(token):
            return mock_user

        async def mock_get_user(user):
            return None

        with (patch('core.security.authentication.jwt_handler.decode', new=mock_decode),
                    patch.object(mock_user_controller, 'get_user', new=mock_get_user)):
            with pytest.raises(UnauthorizedException, match="Unauthorized session"):
                await get_auth_user(mock_request, mock_user_controller)

    def test_paig_okta_verifier(self):
        okta_conf = {
            "enabled": "true",
            "client_id": "test_client_id",
            "audience": "https://test_client_id",
            "issuer": "https://test_client_id"
        }
        obj = PaigOktaVerifier(okta_conf)
        with (patch('requests.post', new={"status_code": 200})):
            assert obj.verify('random_access_token') is not None

        with (patch('requests.post', new={"status_code": 400})):
            try:
                obj.verify('random_access_token')
            except Exception as exc:
                print('exc', exc)
                assert exc.match('Invalid access token')

        with (patch('requests.post', new={"status_code": 200, 'active': False})):
            try:
                obj.verify('random_access_token')
            except Exception as exc:
                assert exc.match('Invalid access token')