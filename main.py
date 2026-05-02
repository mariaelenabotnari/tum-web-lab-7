from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from pydantic import BaseModel
from database import engine
import db_models
from auth import create_access_token, ROLE_PERMISSIONS
from routes.movies import router as movies_router
from routes.comments import router as comments_router

db_models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="CineTrack API",
    description="Movie tracking API with JWT authentication",
    version="1.0.0",
    swagger_ui_parameters={"persistAuthorization": True},
)

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="CineTrack API",
        version="1.0.0",
        description="Movie tracking API with JWT authentication",
        routes=app.routes,
    )
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    }
    openapi_schema["security"] = [{"BearerAuth": []}]
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TokenRequest(BaseModel):
    role: str

@app.post("/token", tags=["auth"])
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

@app.get("/", tags=["auth"])
def root():
    return {"message": "CineTrack API is running"}

app.include_router(movies_router)
app.include_router(comments_router)