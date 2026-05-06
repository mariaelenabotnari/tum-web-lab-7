import os
from datetime import datetime, timezone, timedelta
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

ROLE_PERMISSIONS = {
    "ADMIN":   ["READ", "WRITE", "DELETE"],
    "WRITER":  ["READ", "WRITE"],
    "VISITOR": ["READ"],
}

security = HTTPBearer(
    description="Paste a JWT token. Roles and their permissions:\n\n"
                "- ADMIN -> READ, WRITE, DELETE\n"
                "- WRITER -> READ, WRITE\n"
                "- VISITOR -> READ"
)

def create_access_token(role: str) -> str:
    if role not in ROLE_PERMISSIONS:
        raise HTTPException(status_code=400, detail=f"Invalid role. Must be one of {list(ROLE_PERMISSIONS.keys())}")
    now = datetime.now(timezone.utc)
    payload = {
        "sub": f"user_{role.lower()}",
        "role": role,
        "permissions": ROLE_PERMISSIONS[role],
        "iat": now,
        "exp": now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def decode_token(token: str) -> dict:
    try:
        print(f"DEBUG decoding token...")
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        print(f"DEBUG payload: {payload}")
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if "role" not in payload:
            raise HTTPException(status_code=401, detail="Token missing role")
        if "permissions" not in payload:
            raise HTTPException(status_code=401, detail="Token missing permissions")
        if payload["role"] not in ROLE_PERMISSIONS:
            raise HTTPException(status_code=401, detail="Token has invalid role")
        return payload
    except JWTError as e:
        raise HTTPException(status_code=401, detail=f"Invalid or expired token: {str(e)}")

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    print(f"DEBUG token received: {credentials.credentials[:20]}...")
    return decode_token(credentials.credentials)

def require_permission(permission: str):
    def checker(user=Depends(get_current_user)):
        if permission not in user.get("permissions", []):
            raise HTTPException(status_code=403, detail=f"Permission '{permission}' required")
        return user
    return checker