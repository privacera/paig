from typing import Optional

from pydantic import Field

from core.api_schemas.base_view import BaseView
from core.factory.database_initiator import BaseAPIFilter


class ResponseTemplateView(BaseView):
    """
    A model representing a ResponseTemplate.

    Attributes:
        response (str): The response of the Response Template.
        description (Optional[str]): The description of the Response Template.
    """
    response: str = Field(default=None, description="The response of the Response Template")
    description: Optional[str] = Field(default=None, description="The Description of Response Template")

    model_config = BaseView.model_config


class ResponseTemplateFilter(BaseAPIFilter):
    """
    A model representing a filter for ResponseTemplate.

    Attributes:
        id (int, optional): Filter by ID.
        response (str, optional): Filter by response.
        description (str, optional): Filter by description.
    """

    response: Optional[str] = Field(default=None, description="The response of the Response Template")
    description: Optional[str] = Field(default=None, description="The Description of Response Template")
