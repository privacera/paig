from sqlalchemy import Column, String

from core.db_models.BaseSQLModel import BaseSQLModel


class ResponseTemplateModel(BaseSQLModel):
    """
    SQLAlchemy model representing response template.

    Attributes:
        __tablename__ (str): Name of the database table.
        id (int): Primary key identifier for the record.
        status (int): Status of the record.
        create_time (datetime): Timestamp of creation.
        update_time (datetime): Timestamp of the last update.
        response (str): Response template.
        description (str): Description of response template.
    """

    __tablename__ = "response_template"

    response = Column(String(4000), nullable=False)
    description = Column(String(4000), nullable=True)
