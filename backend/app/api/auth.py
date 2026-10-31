import jwt
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import bearer, current_user
from app.core.database import get_db
from app.core.security import create_token, decode_token, verify_password
from app.models import User
from app.schemas import LoginRequest, TokenPair, UserPublic

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=TokenPair)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.email == data.email.lower()))
    if not user or not user.is_active or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Email hoặc mật khẩu không chính xác.")
    return TokenPair(access_token=create_token(user.id), refresh_token=create_token(user.id, "refresh"), user=user)


@router.post("/refresh", response_model=TokenPair)
def refresh(credentials: HTTPAuthorizationCredentials | None = Depends(bearer), db: Session = Depends(get_db)):
    if not credentials:
        raise HTTPException(status_code=401, detail="Thiếu refresh token.")
    try:
        user_id = decode_token(credentials.credentials, "refresh")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Refresh token không hợp lệ.") from None
    user = db.get(User, user_id)
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="Tài khoản không hoạt động.")
    return TokenPair(access_token=create_token(user.id), refresh_token=create_token(user.id, "refresh"), user=user)


@router.get("/me", response_model=UserPublic)
def me(user: User = Depends(current_user)):
    return user
