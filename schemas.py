from pydantic import BaseModel
from typing import Optional

class SendOTPRequest(BaseModel):
    phone : str

class VerifyOTPRequest(BaseModel):
    phone : str
    otp : str

    class Config:
        from_attributes = True

class TokenResponse(BaseModel):
    token: str
    userId: str
    role: str
    message: str

    class Config:
        from_attributes = True


class AdminLoginRequest(BaseModel):
    username: str
    password: str