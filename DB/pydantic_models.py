from pydantic import BaseModel


class RegisterPayload(BaseModel):
    username: str
    password: str


class LoginPayload(BaseModel):
    username: str
    password: str
