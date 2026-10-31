from datetime import datetime, timedelta, timezone

import jwt
from pwdlib import PasswordHash

from app.core.config import settings

password_hash = PasswordHash.recommended()
ALGORITHM = "HS256"


def hash_password(password: str) -> str:
    return password_hash.hash(password)


def verify_password(password: str, hashed: str) -> bool:
    return password_hash.verify(password, hashed)


def create_token(subject: str, token_type: str = "access") -> str:
    lifetime = timedelta(days=settings.refresh_token_days) if token_type == "refresh" else timedelta(minutes=settings.access_token_minutes)
    payload = {"sub": subject, "type": token_type, "exp": datetime.now(timezone.utc) + lifetime}
    return jwt.encode(payload, settings.secret_key, algorithm=ALGORITHM)


def decode_token(token: str, required_type: str = "access") -> str:
    payload = jwt.decode(token, settings.secret_key, algorithms=[ALGORITHM])
    if payload.get("type") != required_type or not payload.get("sub"):
        raise jwt.InvalidTokenError("Invalid token type")
    return str(payload["sub"])
