from typing import Optional, List

from pydantic import Field, BaseModel

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

        vector_db_id (Optional[int]): The vector databases id with the AI application.
        vector_db_name (Optional[str]): The vector database associated with the AI application.
    """
    name: str = Field(default=None, description="The name of the AI application")
    description: Optional[str] = Field(default=None, description="The description of the AI application")
    application_key: Optional[str] = Field(None, description="The application key", alias="applicationKey")
    vector_dbs: Optional[List[str]] = Field([], description="The vector databases associated with the AI application", alias="vectorDBs")
    guardrail_details: Optional[str] = Field(None, description="The guardrail details", alias="guardrailDetails")
    guardrails: Optional[List[str]] = Field([], description="The guardrails associated with AI application", alias="guardrails")

    vector_db_id: Optional[int] = Field(None, description="The vector databases id with the AI application",
                                        alias="vectorDBId")
    vector_db_name: Optional[str] = Field(None, description="The vector database associated with the AI application",
                                          alias="vectorDBName")

    model_config = BaseView.model_config

    def to_ai_application_data(self):
        from paig_authorizer_core.models.data_models import AIApplicationData

        return AIApplicationData(
            id=self.id,
            status=self.status,
            create_time=self.create_time,
            update_time=self.update_time,
            name=self.name,
            description=self.description,
            application_key=self.application_key,
            vector_db_id=self.vector_db_id,
            vector_db_name=self.vector_db_name
        )


class GuardrailApplicationsAssociation(BaseModel):
    """
    A model representing an AI application guardrail update request.

    Attributes:
        guardrail (str): The guardrail to update.
        applications (List[str]): The applications to update.
    """
    guardrail: str = Field(..., description="The guardrail to update")
    applications: List[str] = Field(..., description="The applications to update")


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
    guardrails: Optional[str] = Field(default=None, description="Filter by guardrail details", alias="guardrail")
