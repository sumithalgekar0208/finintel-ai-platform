from pydantic import BaseModel, EmailStr


class UserRegister(BaseModel):
    email: EmailStr
    full_name: str
    contact_number: str
    hashed_password: str
    is_active: bool = True
    role_id: int


class UserLogin(BaseModel):
    email: EmailStr
    hashed_password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str="bearer"