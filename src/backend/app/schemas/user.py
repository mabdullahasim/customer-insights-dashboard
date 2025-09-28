from pydantic import BaseModel

class UserInDB(BaseModel):
    username: str
    email: str
    hashed_password: str

    model_config = {"from_attributes": True}  # Pydantic v2 replacement for orm_mode

class User(BaseModel):
    username: str
    email: str
    full_name: str
    role: str
    is_active: bool

    model_config = {"from_attributes": True}

# Token model for JWT responses
class Token(BaseModel):
    access_token: str
    token_type: str