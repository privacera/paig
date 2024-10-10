from pydantic import BaseModel


class PostUserLoginRequest(BaseModel):
    user_name: str
    password: str = None


class UserLoginResponse(BaseModel):
    user_id: int
    user_name: str
