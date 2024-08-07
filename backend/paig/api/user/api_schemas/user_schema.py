from pydantic import BaseModel, Field, field_validator, validate_email
from typing import Literal, List, Optional
import api.user.constants as user_constants
import re
from core.factory.database_initiator import BaseAPIFilter


def _validate_password(value):
    pattern = r'^$|^(?=.*[A-Za-z])(?=.*\d).{8,255}$'
    regex = re.compile(pattern)
    if regex.fullmatch(value):
        return value
    else:
        raise ValueError("Password should contain. One letter, One number and at least 8 characters long.")


def _validate_email(value):
    if value is not None and value.strip() != "":
        validate_email(value)
        value = value.strip().lower()
    return value


def _validate_username(value):
    pattern = r"^[a-zA-Z0-9_.-]{1,255}$"
    regex = re.compile(pattern)
    if regex.fullmatch(value):
        return value.strip().lower()
    else:
        raise ValueError("Invalid username")


class BaseUserModel(BaseModel):
    status: Optional[Literal[0, 1]] = Field(1, description="User status 0 or 1")
    first_name: str = Field(..., description="First Name of the user", pattern=r"^[a-zA-Z0-9_'.-]{2,255}$", examples=["John"], alias="firstName")
    last_name: Optional[str] = Field(None, description="Last Name of the user", pattern=r"^[a-zA-Z0-9_'.-]*$", examples=["Doe"], alias="lastName")
    email: str | None = Field(default=None, description="Email id of the user")
    password: str = Field(default="", description="User Password")
    roles: List[Literal[user_constants.OWNER_ROLE, user_constants.USER_ROLE]] = Field(..., description="Invalid user role", examples=[["USER"]])
    groups: List[str] = Field(default=[], description="List of group names", examples=[[]])

    @field_validator("password")
    def validate_password(cls, value):
        return _validate_password(value)

    @field_validator("email")
    def validate_email(cls, value):
        return _validate_email(value)


class UsernameModel(BaseModel):
    username: str = Field(None, description="Unique username of the user", examples=["JohnDoe"])

    @field_validator("username")
    def validate_username(cls, value):
        return _validate_username(value)


class UpdateUserModel(BaseUserModel):
    pass


class CreateUserModel(BaseUserModel, UsernameModel):
    pass


class UserLoginResponse(UsernameModel):
    id: int | None = Field(..., description="User Id")


class UserLoginRequest(UsernameModel):
    password: str = Field(..., description="User Password")

    @field_validator("password")
    def validate_password(cls, value):
        return _validate_password(value)


class GetUsersFilterRequest(BaseAPIFilter):
    """
    A model representing a filter for users

    Attributes:
        username (Optional[str]): The username of the user.
        firstName (Optional[str]): The first name of the user.
        lastName (Optional[str]): The last name of the user.
        email (Optional[str]): The email of the user.
    """
    first_name: Optional[str] = Field(None, description="First name of the user", pattern=r"^([a-zA-Z0-9,_'.-]*)?$", alias="firstName")
    last_name: Optional[str] = Field(None, description="Last name of the user", pattern=r"^([a-zA-Z0-9,_'.-]*)?$", alias="lastName")
    email: Optional[str] = Field(None, description="Email of the user")
    username: Optional[str] = Field(None, description="Unique username of the user", pattern=r"^([a-zA-Z0-9,_.-]{1,255})?$",
                          examples=["JohnDoe"])
