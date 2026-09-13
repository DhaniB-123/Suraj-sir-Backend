from fastapi import APIRouter,Depends,HTTPException,status
from app.schemas import SendOTPRequest, VerifyOTPRequest, TokenResponse, AdminLoginRequest
from sqlalchemy.orm import Session
from app.models import User
from app.database import get_db
from datetime import datetime, timedelta
from dotenv import load_dotenv
from jose import jwt
import os
from firebase_admin import credentials, auth
import firebase_admin 


load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
EXPIRE_DAYS = int(os.getenv("ACCESS_TOKEN_EXPIRE_DAYS"))

def create_access_token(data: dict):
    expire = datetime.utcnow() + timedelta(days=EXPIRE_DAYS)
    data.update({"exp": expire})
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)

cred = credentials.Certificate("firebase-credentials.json")
firebase_admin.initialize_app(cred)

router = APIRouter(prefix="/auth",tags=["Authentication"])
@router.post("/send-otp")
async def send_otp(request : SendOTPRequest,db : Session = Depends(get_db)):
    try:
        phone_number = f"+92{request.phone.lstrip('0')}"
        try:
            auth.create_user(phone_number = phone_number)
        except Exception:
            pass

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail="There is an error please Try again!")

    return {"message" : "OTP sent Successfully to this phone number","phone" : phone_number}

@router.post("/verify-otp", response_model=TokenResponse)
async def verify_otp(request: VerifyOTPRequest, db: Session = Depends(get_db)):
    # Dev mode - sirf 123456 check karo
    if request.otp != "123456":
        raise HTTPException(status_code=400, detail="Invalid OTP")
    
    user = db.query(User).filter(User.phone == request.phone).first()
    if not user:
        user = User(phone=request.phone, role="student")
        db.add(user)
        db.commit()
        db.refresh(user)
    
    token = create_access_token({"sub": str(user.id), "role": user.role})
    
    return TokenResponse(
        token=token,
        userId=str(user.id),
        role=user.role,
        message="Login successful"
    )
    # except Exception as e:
    #     raise HTTPException(status_code=400, detail="Invalid OTP")

@router.post("/admin/login")
async def admin_login(request : AdminLoginRequest,db : Session = Depends(get_db)):
    user = db.query(User).filter(User.username == request.username).first()
    if not user or user.role != "admin":
        raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST,detail = "invalid credentials")
    if request.password != user.password:
        raise HTTPException(status_code= status.HTTP_400_BAD_REQUEST,detail = "invalid credentials")
    
    token = create_access_token({"sub" : str(user.id),"role" : user.role})

    return TokenResponse(
        token = token,
        userId = str(user.id),
        role = user.role,
        message = "admin login successfully"
    )