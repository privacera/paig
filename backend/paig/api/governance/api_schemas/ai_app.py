from typing import Optional, List

from pydantic import Field

from core.factory.database_initiator import BaseAPIFilter
from core.api_schemas.base_view import BaseView


class AIApplicationView(BaseView):
    """
    A model representing an AI application.

    Inherits from:
        BaseView: The base model containing common fields.

    Attributes:
        name (str): The name of the AI application.
        description (str): The description of the AI application.
        application_key (str): The application key.
        vector_dbs (Optional[str]): The vector databases associated with the AI application.
    """
    name: str = Field(default=None, description="The name of the AI application")
    description: Optional[str] = Field(default=None, description="The description of the AI application")
    application_key: Optional[str] = Field(None, description="The application key", alias="applicationKey")
    vector_dbs: Optional[List[str]] = Field([], description="The vector databases associated with the AI application", alias="vectorDBs")

    class Config(BaseView.Config):
        pass


class AIApplicationFilter(BaseAPIFilter):
    """
    Filter class for AI application queries.

    Attributes:
        id (int, optional): Filter by ID.
        name (str, optional): Filter by name.
        application_key (str, optional): Filter by application key.
        vector_dbs (str, optional): Filter by vector db.
    """

    id: Optional[int] = Field(default=None, description="Filter by id")
    name: Optional[str] = Field(default=None, description="Filter by name")
    application_key: Optional[str] = Field(default=None, description="Filter by application key", alias="applicationKey")
    vector_dbs: Optional[str] = Field(default=None, description="Filter by vector db", alias="vectorDB")
