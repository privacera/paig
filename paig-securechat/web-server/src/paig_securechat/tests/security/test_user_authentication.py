import pytest
import base64
from unittest.mock import AsyncMock, patch
from fastapi import Request
from core.security.authentication import get_auth_user, authorize_credentials_with_df
from core.exceptions import UnauthorizedException
from core.security.okta_verifier import PaigOktaVerifier
import pandas as pd
from werkzeug.security import generate_password_hash

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

        # Mock the DataFrame used by the function to validate credentials
        mock_df = pd.DataFrame({
            "Username": ["valid_user"],
            "Secrets": [generate_password_hash("valid_password")]
        })
        with patch('core.security.authentication.constants.USER_SECRETS_DF', mock_df):
            with patch("core.security.authentication.__validate_basic_auth", new=AsyncMock(return_value={"user_name": "valid_user"})):
                result = await get_auth_user(request, user_controller_mock)
                assert result["user_name"] == "valid_user"

    @pytest.mark.asyncio
    async def test_get_auth_user_basic_auth_invalid_username(self):
        user_controller_mock = AsyncMock()
        user_controller_mock.get_user_by_user_name.return_value = None

        invalid_credentials = base64.b64encode(b"invalid_user:valid_password").decode("utf-8")

        # Add 'type' to the scope to make it a valid HTTP request
        request = Request(scope={
            "type": "http",  
            "headers": [(b"authorization", f"Basic {invalid_credentials}".encode("utf-8"))]
        })

        # Mock the DataFrame used by the function to validate credentials
        mock_df = pd.DataFrame({
            "Username": ["valid_user"],
            "Secrets": [generate_password_hash("valid_password")]
        })
        with patch('core.security.authentication.constants.USER_SECRETS_DF', mock_df):
            with pytest.raises(UnauthorizedException):
                await get_auth_user(request, user_controller_mock)

    @pytest.mark.asyncio
    async def test_get_auth_user_basic_auth_invalid_password(self):
        user_controller_mock = AsyncMock()
        user_controller_mock.get_user_by_user_name.return_value = {"user_name": "valid_user"}

        invalid_credentials = base64.b64encode(b"valid_user:wrong_password").decode("utf-8")

        
        request = Request(scope={
            "type": "http",  
            "headers": [(b"authorization", f"Basic {invalid_credentials}".encode("utf-8"))]
        })

        # Mock the DataFrame used by the function to validate credentials
        mock_df = pd.DataFrame({
            "Username": ["valid_user"],
            "Secrets": [generate_password_hash("valid_password")]
        })
        with patch('core.security.authentication.constants.USER_SECRETS_DF', mock_df):
            with pytest.raises(UnauthorizedException):
                await get_auth_user(request, user_controller_mock)

    def test_authorize_credentials_with_valid_user(self):
        mock_df = pd.DataFrame({
            "Username": ["valid_user"],
            "Secrets": [generate_password_hash("valid_password")]
        })

        with patch('core.security.authentication.constants.USER_SECRETS_DF', mock_df):
            authorize_credentials_with_df("valid_user", "valid_password")  # Should not raise an exception

    def test_authorize_credentials_with_invalid_username(self):
        mock_df = pd.DataFrame({
            "Username": ["valid_user"],
            "Secrets": [generate_password_hash("valid_password")]
        })

        with patch('core.security.authentication.constants.USER_SECRETS_DF', mock_df):
            with pytest.raises(UnauthorizedException, match="Invalid username or password"):
                authorize_credentials_with_df("invalid_user", "valid_password")

    def test_authorize_credentials_with_invalid_password(self):
        mock_df = pd.DataFrame({
            "Username": ["valid_user"],
            "Secrets": [generate_password_hash("valid_password")]
        })

        with patch('core.security.authentication.constants.USER_SECRETS_DF', mock_df):
            with pytest.raises(UnauthorizedException, match="Invalid username or password"):
                authorize_credentials_with_df("valid_user", "wrong_password")

    def test_authorize_credentials_with_empty_df(self):
        mock_df = pd.DataFrame(columns=["Username", "Secrets"])

        with patch('core.security.authentication.constants.USER_SECRETS_DF', mock_df):
            with pytest.raises(UnauthorizedException, match="User authentication data not available"):

                authorize_credentials_with_df("valid_user", "valid_password")

    def test_authorize_credentials_with_missing_columns(self):
        mock_df = pd.DataFrame({"User": ["valid_user"], "Secret": [generate_password_hash("valid_password")]})

        with patch('core.security.authentication.constants.USER_SECRETS_DF', mock_df):
            with pytest.raises(UnauthorizedException, match="User authentication data format error"):
                authorize_credentials_with_df("valid_user", "valid_password")
            

                
