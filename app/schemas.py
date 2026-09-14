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



class ContentUploadRequest(BaseModel):
    title: str
    type: str
    url: str
    topic_id: str
    is_free: bool = False
    price: int = 0

class UnlockRequestResponse(BaseModel):
    id: str
    user_id: str
    content_id: str
    status: str
    amount: int = 0
    created_at: str

    class Config:
        from_attributes = True
