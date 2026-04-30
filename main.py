from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from database import engine
import db_models
from auth import create_access_token, ROLE_PERMISSIONS
from routes.movies import router as movies_router

db_models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="CineTrack API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TokenRequest(BaseModel):
    role: str

@app.post("/token")
def get_token(request: TokenRequest):
    if request.role not in ROLE_PERMISSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Role must be one of {list(ROLE_PERMISSIONS.keys())}"
        )
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

app.include_router(movies_router)