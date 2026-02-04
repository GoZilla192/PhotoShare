from pydantic import BaseModel, EmailStr, field_validator

class RegisterRequest(BaseModel):
    username: str
    email: EmailStr
    password: str
    confirm_password: str

    @field_validator("confirm_password")
    @classmethod
    def password_match(cls, v, info):
        if v != info.data.get("password"):
            raise ValueError("Password do not match")
        return v

class LoginRequest(BaseModel):
    email: EmailStr
    password: str