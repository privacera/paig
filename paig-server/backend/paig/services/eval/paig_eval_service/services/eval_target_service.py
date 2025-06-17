import copy
import json
import traceback
import asyncio
import httpx
from core.utils import SingletonDepends, is_valid_url, clean_headers
from core import config
from ..database.db_operations.eval_target_repository import EvaluationTargetRepository
import logging
from core.exceptions import NotFoundException, InternalServerError, BadRequestException
from core.controllers.paginated_response import create_pageable_response
from core.db_session.transactional import Transactional, Propagation
from ..factory.crypto_factory import get_crypto_service
from ..utility import encrypt_target_creds, decrypt_target_creds

logger = logging.getLogger(__name__)

crypto_service = get_crypto_service()


async def transform_eval_target(eval_target):
    eval_target_dict = dict()
    if not is_valid_url(eval_target['url']):
        raise BadRequestException("Invalid URL format")
    eval_target_dict['id'] = eval_target['url']
    eval_target_dict['label'] = eval_target["name"]
    eval_config = dict()
    eval_config['method'] = eval_target['method']
    if isinstance(eval_target['headers'], dict):
        eval_config['headers'] = eval_target['headers']
    else:
        try:
            eval_target['headers'] = json.loads(eval_target['headers'])
        except Exception as e:
            raise BadRequestException("Invalid headers format")
    if isinstance(eval_target['body'], dict):
        eval_config['body'] = eval_target['body']
    else:
        try:
            eval_config['body'] = json.loads(eval_target['body'])
        except Exception as e:
            raise BadRequestException("Invalid body format")
    eval_config['transformResponse'] = eval_target['transformResponse']
    eval_config['headers'] = {k: v for k, v in eval_config['headers'].items() if k and v}
    eval_config['headers'] = await encrypt_target_creds(eval_config['headers'])
    eval_target_dict['config'] = eval_config
    return json.dumps(eval_target_dict)

async def transform_eval_target_to_dict(config):
    target = json.loads(config)
    config = target.get('config', {})
    eval_taget_config = dict()
    eval_taget_config['method'] = config.get('method', '')
    eval_taget_config['headers'] = await decrypt_target_creds(config.get('headers', {}))
    eval_taget_config['body'] = config.get('body', {})
    eval_taget_config['transformResponse'] = config.get('transformResponse', '')
    eval_taget_config['url'] = target.get('id', '')
    return eval_taget_config

class EvaluationTargetService:

    def __init__(self,
        eval_target_repository: EvaluationTargetRepository = SingletonDepends(EvaluationTargetRepository)
    ):
        self.eval_target_repository = eval_target_repository

    async def get_all_ai_app_with_host(self, include_filters, exclude_filters, page_number, size, sort):
        if include_filters.name:
            include_filters.name = include_filters.name.strip("*")
        if exclude_filters.name:
            exclude_filters.name = exclude_filters.name.strip("*")
        ai_apps, total_count = await self.eval_target_repository.get_application_list_with_filters(include_filters,
                                                                                                   exclude_filters,
                                                                                                   page_number, size,
                                                                                                   sort, min_value=None,
                                                                                                   max_value=None)
        if ai_apps is None:
            raise NotFoundException("No applications found")
        try:
            final_apps = list()
            for ai_app in ai_apps:
                app = dict()
                app['id'] = ai_app.id
                app['ai_application_id'] = ai_app.application_id
                app['target_id'] = ai_app.id
                app['url'] = ai_app.url
                app['name'] = ai_app.name
                app['status'] = ai_app.status
                final_apps.append(app)
            return create_pageable_response(final_apps, total_count, page_number, size, sort)
        except Exception as e:
            logger.error(f"Error in get_all_ai_app_with_host: {e}")
            logger.error(traceback.format_exc())
            raise InternalServerError("Internal server error")

    @Transactional(propagation=Propagation.REQUIRED)
    async def create_app_target(self, body_params):
        new_params = dict()

        transformed_eval = await transform_eval_target(body_params)
        new_params['config'] = transformed_eval
        new_params['name'] = body_params['name']
        new_params['url'] = body_params['url']
        new_params['target_user'] = body_params['username']
        new_params['status'] = 'ACTIVE'
        if 'ai_application_id' in body_params and body_params['ai_application_id']:
            new_params['application_id'] = body_params['ai_application_id']

        name_exists = await self.eval_target_repository.application_name_exists(body_params['name'])
        if name_exists:
            raise BadRequestException(f"Application with name {body_params['name']} already exists")
        eval_target = await self.eval_target_repository.create_app_target(new_params)
        return eval_target


    @Transactional(propagation=Propagation.REQUIRED)
    async def update_app_target(self, target_id, body_params):
        new_params = dict()
        target_model = await self.eval_target_repository.get_target_by_id(target_id)
        if target_model is None:
            raise NotFoundException(f"No application found with id {target_id}")
        if target_model.application_id:
            body_params['name'] = target_model.name
        else:
            if 'name' in body_params and body_params['name'] != target_model.name:
                name_exists = await self.eval_target_repository.application_name_exists(body_params['name'])
                if name_exists:
                    raise BadRequestException(f"Application with name {body_params['name']} already exists")
        transformed_eval = await transform_eval_target(body_params)
        new_params['config'] = transformed_eval
        new_params['url'] = body_params['url']
        new_params['status'] = 'ACTIVE'
        if 'name' in body_params:
            new_params['name'] = body_params['name']
        if 'username' in body_params:
            new_params['target_user'] = body_params['username']
        try:
            eval_target = await self.eval_target_repository.update_app_target(new_params, target_model)
            eval_target_resp = copy.deepcopy(eval_target.__dict__)
            eval_target_resp['username'] = eval_target_resp.pop('target_user')
            return eval_target_resp
        except Exception as e:
            logger.error(f"Error in update_app_target: {e}")
            logger.error(traceback.format_exc())
            raise InternalServerError("Internal server error")

    @Transactional(propagation=Propagation.REQUIRED)
    async def delete_target(self, app_id):
        target_model = await self.eval_target_repository.get_target_by_id(app_id)
        if target_model is None:
            raise NotFoundException(f"No application found with id {app_id}")
        try:
            eval_target = await self.eval_target_repository.delete_target(target_model)
            return eval_target
        except Exception as e:
            logger.error(f"Error in delete_target: {e}")
            logger.error(traceback.format_exc())
            raise InternalServerError("Internal server error")

    async def get_app_target_by_id(self, app_id):
        target_model = await self.eval_target_repository.get_target_by_id(app_id)
        if target_model is None:
            raise NotFoundException(f"No application found with id {app_id}")
        try:
            resp = dict()
            resp['config'] = await transform_eval_target_to_dict(target_model.config)
            resp['name'] = target_model.name
            resp['url'] = target_model.url
            resp['id'] = target_model.id
            resp['target_id'] = target_model.id
            resp['ai_application_id'] = target_model.application_id
            resp['username'] = target_model.target_user
            resp['status'] = target_model.status
            return resp
        except Exception as e:
            logger.error(f"Error in get_app_target_by_id: {e}")
            logger.error(traceback.format_exc())
            raise InternalServerError("Internal server error")

    @Transactional(propagation=Propagation.REQUIRED)
    async def update_app_target_on_ai_app(self, ai_app_id, ai_app_name):
        # check for existing target
        target_model = await self.eval_target_repository.get_target_by_app_id(ai_app_id)
        if target_model is not None:
            target_model.name = ai_app_name
            return await self.eval_target_repository.update_app_target({'name': ai_app_name}, target_model)
        new_params = dict()
        new_params['application_id'] = ai_app_id
        new_params['name'] = ai_app_name
        new_params['url'] = None
        new_params['config'] = "{}"
        try:
            eval_target = await self.eval_target_repository.create_app_target(new_params)
            return eval_target
        except Exception as e:
            logger.error(f"Error in insert_app_target_on_ai_app: {e}")
            logger.error(traceback.format_exc())
            raise InternalServerError("Internal server error")

    @Transactional(propagation=Propagation.REQUIRED)
    async def delete_app_target_on_ai_app(self, ai_app_id):
        # check for existing target
        target_model = await self.eval_target_repository.get_target_by_app_id(ai_app_id)
        if target_model is None:
            return
        try:
            eval_target = await self.eval_target_repository.delete_target(target_model)
            return eval_target
        except Exception as e:
            logger.error(f"Error in delete_app_target_on_ai_app: {e}")
            logger.error(traceback.format_exc())
            raise InternalServerError("Internal server error")

    async def check_target_application_connection(self, body_params: dict):
        """
        Check the connection of the target application by making a test request.
        
        Args:
            body_params (dict): Dictionary containing connection parameters
                - url: Target application URL (validated by Pydantic)
                - method: HTTP method (GET, POST, etc.)
                - headers: Request headers (validated by Pydantic)
                - body: Request body (validated by Pydantic)
        
        Returns:
            dict: Connection test result with status and message
        
        Raises:
            InternalServerError: If connection test fails
        """
        timeout = config.Config.get('target_application_connection_timeout', 60)
        client = httpx.AsyncClient(timeout=timeout)
        
        try:
            # Request parameters are already validated by Pydantic schema
            url = body_params['url']
            method = body_params.get('method', 'POST').upper()
            headers = clean_headers(body_params.get('headers', {}))
            body = body_params.get('body', {})

            response = await client.request(method, url, headers=headers, json=body)

            if 200 <= response.status_code < 300:
                return {
                    "status": "success",
                    "message": "Successfully connected to the target application",
                    "status_code": response.status_code
                }
            
            # Handle non-success status codes
            error_message = self._extract_error_message(response.text)
            return {
                "status": "error",
                "message": f"Connection failed: {error_message}",
                "status_code": response.status_code
            }

        except httpx.RequestError as e:
            return {
                "status": "error",
                "message": f"Connection failed: {str(e)}",
                "status_code": 502
            }
        except asyncio.TimeoutError:
            return {
                "status": "error",
                "message": "Connection timed out after 60 seconds",
                "status_code": 504
            }
        except Exception as e:
            logger.error(f"Error in check_target_application_connection: {e}")
            raise InternalServerError(f"Failed to test connection: {str(e)}")
        finally:
            await client.aclose()

    def _extract_error_message(self, response_text: str) -> str:
        """
        Extract error message from response text.
        
        Args:
            response_text: The response text from the target application
            
        Returns:
            str: Extracted error message or original text if parsing fails
        """
        if not response_text:
            return "No response from server"
        
        try:
            error_json = json.loads(response_text)
            return error_json.get("message", response_text)
        except json.JSONDecodeError:
            return response_text
        