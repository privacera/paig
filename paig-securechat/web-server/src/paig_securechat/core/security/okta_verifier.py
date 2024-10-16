import requests
from urllib.parse import urlparse
import logging
from okta_jwt_verifier import AccessTokenVerifier
logger = logging.getLogger(__name__)


class PaigOktaVerifier:
    def __init__(self,
                 okta_conf: dict
                 ):
        self.okta_conf = okta_conf
        self.issuer = okta_conf['issuer']
        self.audience = okta_conf['audience']
        self.client_id = okta_conf['client_id']
        self.base_url = self.__base_url(self.issuer)
        self.is_custom_auth_server = self.base_url != self.audience
        if self.is_custom_auth_server:
            """
            Whenever the audience is organization itself, it is considered as default auth server.
            Public keys are opaque for default auth server and it is not possible to verify the access token
            locally using okta_jwt_verifier library.
            """
            logger.info(f"Custom auth server is enabled.Intializating custom auth server verifier.")
            self.custom_auth_jwt_verifier = AccessTokenVerifier(issuer=self.issuer, audience=self.audience)

    @staticmethod
    def __base_url(url):
        parse_url = urlparse(url)
        return f"{parse_url.scheme}://{parse_url.netloc}"

    async def verify(self, access_token):
        if self.is_custom_auth_server:
            logger.info(f"Verifying access token with custom auth server")
            return await self.__verify_custom_auth_access_token(access_token)
        else:
            logger.info(f"Verifying access token with default auth server")
            return await self.__verify_default_auth_access_token(access_token)

    async def __verify_custom_auth_access_token(self, access_token):
        await self.custom_auth_jwt_verifier.verify(access_token)

    async def __verify_default_auth_access_token(self, access_token):
        """
        In case of default auth server, we need to verify the access token using introspect endpoint.
        """
        data = f'token={access_token}&token_type_hint=access_token'
        url = f"{self.base_url}/oauth2/v1/introspect?client_id={self.client_id}"
        if self.okta_conf.get('introspect_endpoint') and self.okta_conf.get('introspect_endpoint') != "":
            url = self.okta_conf.get('introspect_endpoint')
            logger.info(f"Using introspect endpoint from config: {url}")
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        resp = requests.post(url, data=data, headers=headers)
        if resp.status_code != 200:
            logger.error(f"Error in verify: {resp.text}")
            raise Exception("Invalid access token")

        json_resp = resp.json()
        if json_resp.get('active') is not True:
            logger.error(f"Access token is not active")
            raise Exception("Invalid access token")
        return json_resp