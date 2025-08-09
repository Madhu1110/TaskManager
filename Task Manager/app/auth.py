# app/auth.py
from fastapi import Depends, HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt, os
from typing import Optional

JWT_SECRET = os.getenv("JWT_SECRET", "change-me")
JWT_ALGO = "HS256"
security = HTTPBearer(auto_error=False)

def create_access_token(payload: dict, expire_minutes: int = 60*24*7):
    import datetime
    to_encode = payload.copy()
    to_encode.update({"exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=expire_minutes)})
    return jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGO)

def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGO])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")

def get_current_user_id(credentials: Optional[HTTPAuthorizationCredentials] = Security(security)):
    if credentials is None:
        raise HTTPException(status_code=401, detail="Not authenticated")
    token = credentials.credentials
    payload = decode_token(token)
    user_id = payload.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token payload")
    return user_id


