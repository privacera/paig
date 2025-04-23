from sqlalchemy.exc import NoResultFound

from api.guardrails import ResponseTemplateType
from api.guardrails.api_schemas.response_template import ResponseTemplateView
from core.exceptions import NotFoundException
from core.exceptions.error_messages_parser import get_error_message, ERROR_RESOURCE_NOT_FOUND
from core.factory.database_initiator import BaseOperations
from api.guardrails.database.db_models.response_template_model import ResponseTemplateModel


class ResponseTemplateRepository(BaseOperations[ResponseTemplateModel]):
    """
    Repository class for handling database operations related to ResponseTemplate models.

    Inherits from BaseOperations[ResponseTemplateModel], providing generic CRUD operations.

    This class inherits all methods from BaseOperations[ResponseTemplateModel].
    """

    def __init__(self):
        """
        Initialize the ResponseTemplateRepository.
        """
        super().__init__(ResponseTemplateModel)

    async def get_response_templates_by_id(self, id) -> ResponseTemplateView:
        filters = {"id": id, "type": ResponseTemplateType.SYSTEM_DEFINED, "or_column_list": "tenant_id,type"}
        try:
            return await self.get_by(
                filters=filters,
                unique=True
            )
        except NoResultFound as e:
            raise NotFoundException(get_error_message(ERROR_RESOURCE_NOT_FOUND, "Response Template", "id", [id]), e)
