from pydantic import BaseModel, field_validator
import re

class User(BaseModel):
    id: int 
    username: str
    email: str
    role: str
    is_active: bool

    model_config = {"from_attributes": True}

class UserInDB(User):
    hashed_password: str

    model_config = {"from_attributes": True}

class UserCreate(BaseModel):
    username: str
    email: str
    password: str

    @field_validator("username")
    def check_username(cls, v: str) -> str:
        if not re.match(r'^[a-zA-Z0-9_]{8,12}$', v):
            raise ValueError("Username must be 8–12 characters, letters/numbers/underscores only")
        return v

class UserRead(BaseModel):
    username: str
    email: str
    is_active: bool

class UserUpdate(BaseModel):
    username: str
    email: str
    hashed_password: str
    
# Token model for JWT responses
class Token(BaseModel):
    access_token: str
    token_type: str

class ForgotPassword(BaseModel):
    email: str
    password: str
