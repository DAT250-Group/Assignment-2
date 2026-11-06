from pydantic import BaseModel
from typing import Optional

class LoginSchema(BaseModel):
    email: str
    password: str

class RegisterSchema(BaseModel):
    email: str
    full_name: str
    password: str

class UserUpdateSchema(BaseModel):
    email: Optional[str] = None
    full_name: Optional[str] = None