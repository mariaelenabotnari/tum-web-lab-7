from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from auth import create_access_token, decode_token, ROLE_PERMISSIONS

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
    if request.role not in ["ADMIN", "WRITER", "VISITOR"]:
        raise HTTPException(status_code=400, detail="Role must be ADMIN, WRITER or VISITOR")

    token = create_access_token(role=request.role)

    return {
        "access_token": token,
        "token_type": "bearer",
        "role": request.role,
        "permissions": ROLE_PERMISSIONS[request.role]
    }

@app.get("/")
def root():
    return {"message": "CineTrack API is running"}