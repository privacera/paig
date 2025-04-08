import pytest
import base64
from fastapi import Request
from unittest.mock import AsyncMock, patch
import pandas as pd

from core.exceptions import UnauthorizedException
from core.security.authentication import get_auth_user
from core.security.okta_verifier import PaigOktaVerifier
from services.user_data_service import UserDataService



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

        with (
            patch('core.security.authentication.jwt_handler.decode', new=mock_decode),
            patch.object(mock_user_controller, 'get_user', new=mock_get_user)
        ):
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
               assert exc.match('Invalid access token')

        with (patch('requests.post', new={"status_code": 200, 'active': False})):
            try:
                obj.verify('random_access_token')
            except Exception as exc:
                 assert exc.match('Invalid access token')

    @pytest.mark.asyncio
    async def test_get_auth_user_basic_auth_valid(self):
        user_controller_mock = AsyncMock()
        user_controller_mock.get_user_by_user_name.return_value = {"user_name": "valid_user"}

        valid_credentials = base64.b64encode(b"valid_user:valid_password").decode("utf-8")

        request = Request(scope={
            "type": "http",
            "headers": [(b"authorization", f"Basic {valid_credentials}".encode("utf-8"))]
        })

        with patch('core.security.authentication.user_details_service.verify_user_credentials', return_value=True), \
             patch('core.security.authentication.basic_auth_enabled', True):
            result = await get_auth_user(request, user_controller_mock)
            assert result["user_name"] == "valid_user"

    @pytest.mark.asyncio
    async def test_get_auth_user_basic_auth_invalid_credentials(self):
        user_controller_mock = AsyncMock()
        user_controller_mock.get_user_by_user_name.return_value = None

        invalid_credentials = base64.b64encode(b"invalid_user:wrong_password").decode("utf-8")

        request = Request(scope={
            "type": "http",
            "headers": [(b"authorization", f"Basic {invalid_credentials}".encode("utf-8"))]
        })

        with patch('core.security.authentication.user_details_service.verify_user_credentials', side_effect=UnauthorizedException("Invalid credentials")), \
             patch('core.security.authentication.basic_auth_enabled', True):
            with pytest.raises(UnauthorizedException, match="Invalid credentials"):
                await get_auth_user(request, user_controller_mock)


@pytest.fixture
def mock_user_data():
    return pd.DataFrame({
        "Username": ["test_user"],
        "Secrets": ["pbkdf2:sha256:260000$abc$1234567890abcdef"]
    })


@patch("services.user_data_service.check_password_hash")
def test_verify_user_credentials_success(mock_check_hash, mock_user_data):
    mock_check_hash.return_value = True
    uds = UserDataService()
    uds.user_data = mock_user_data

    result = uds.verify_user_credentials("test_user", "password123")
    assert result == {"user_name": "test_user"}
    mock_check_hash.assert_called_once()


def test_verify_user_credentials_invalid_user(mock_user_data):
    uds = UserDataService()
    uds.user_data = mock_user_data

    with pytest.raises(UnauthorizedException, match="Invalid user_name or password"):
        uds.verify_user_credentials("invalid_user", "password123")


def test_verify_user_credentials_missing_password(mock_user_data):
    uds = UserDataService()
    uds.user_data = mock_user_data

    with pytest.raises(UnauthorizedException, match="Invalid user_name or password"):
        uds.verify_user_credentials("test_user", "")


@patch("services.user_data_service.check_password_hash")
def test_verify_user_credentials_wrong_password(mock_check_hash, mock_user_data):
    mock_check_hash.return_value = False
    uds = UserDataService()
    uds.user_data = mock_user_data

    with pytest.raises(UnauthorizedException, match="Invalid user_name or password"):
        uds.verify_user_credentials("test_user", "wrongpass")
