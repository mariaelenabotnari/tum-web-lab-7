from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from auth import create_access_token

app = FastAPI(title="CineTrack API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TokenRequest(BaseModel):
    role: str  # "ADMIN" | "WRITER" | "VISITOR"

@app.post("/token")
def get_token(request: TokenRequest):
    allowed_roles = ["ADMIN", "WRITER", "VISITOR"]
    if request.role not in allowed_roles:
        raise HTTPException(status_code=400, detail=f"Role must be one of {allowed_roles}")

    permissions = {
        "ADMIN":   ["READ", "WRITE", "DELETE"],
        "WRITER":  ["READ", "WRITE"],
        "VISITOR": ["READ"],
    }

    token = create_access_token({
        "role": request.role,
        "permissions": permissions[request.role]
    })

    return {
        "access_token": token,
        "token_type": "bearer",
        "role": request.role,
        "permissions": permissions[request.role]
    }

@app.get("/")
def root():
    return {"message": "CineTrack API is running"}