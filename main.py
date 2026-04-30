from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
from auth import create_access_token, decode_token, ROLE_PERMISSIONS
from models import Movie, MovieCreate, MovieUpdate, Comment
import database

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

def get_current_user(authorization: str = Header(...)):
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization header")
    token = authorization.split(" ")[1]
    payload = decode_token(token)  # no need to check None anymore
    return payload

def require_permission(permission: str):
    def checker(user=Depends(get_current_user)):
        if permission not in user.get("permissions", []):
            raise HTTPException(status_code=403, detail=f"Permission '{permission}' required")
        return user
    return checker

@app.post("/token")
def get_token(request: TokenRequest):
    if request.role not in ROLE_PERMISSIONS:
        raise HTTPException(status_code=400, detail=f"Role must be one of {list(ROLE_PERMISSIONS.keys())}")

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

@app.get("/movies", response_model=List[Movie])
def get_movies(
    skip: int = 0,
    limit: int = 10,
    search: Optional[str] = None,
    genre: Optional[str] = None,
    min_rating: Optional[float] = None,
    max_rating: Optional[float] = None,
    is_favorite: Optional[bool] = None,
    user=Depends(require_permission("READ"))
):
    results = database.movies_db

    if search:
        results = [m for m in results if search.lower() in m.title.lower()]

    if genre:
        results = [m for m in results if m.genre.lower() == genre.lower()]

    if min_rating is not None:
        results = [m for m in results if m.rating is not None and m.rating >= min_rating]

    if max_rating is not None:
        results = [m for m in results if m.rating is not None and m.rating <= max_rating]

    if is_favorite is not None:
        results = [m for m in results if m.isFavorite == is_favorite]

    return results[skip: skip + limit]

@app.get("/movies/{movie_id}", response_model=Movie)
def get_movie(
    movie_id: int,
    user=Depends(require_permission("READ"))
):
    movie = next((m for m in database.movies_db if m.id == movie_id), None)
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    return movie

@app.post("/movies", response_model=Movie, status_code=201)
def create_movie(
    movie: MovieCreate,
    user=Depends(require_permission("WRITE"))
):
    new_movie = Movie(id=database.next_id, **movie.dict())
    database.next_id += 1
    database.movies_db.append(new_movie)
    return new_movie

@app.put("/movies/{movie_id}", response_model=Movie)
def update_movie(
    movie_id: int,
    updates: MovieUpdate,
    user=Depends(require_permission("WRITE"))
):
    movie = next((m for m in database.movies_db if m.id == movie_id), None)
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")

    updated = movie.dict()
    for key, value in updates.dict(exclude_unset=True).items():
        updated[key] = value

    idx = database.movies_db.index(movie)
    database.movies_db[idx] = Movie(**updated)
    return database.movies_db[idx]

@app.delete("/movies/{movie_id}", status_code=204)
def delete_movie(
    movie_id: int,
    user=Depends(require_permission("DELETE"))
):
    movie = next((m for m in database.movies_db if m.id == movie_id), None)
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    database.movies_db.remove(movie)
    return None

@app.get("/movies/{movie_id}/comments", response_model=List[Comment])
def get_comments(
    movie_id: int,
    user=Depends(require_permission("READ"))
):
    movie = next((m for m in database.movies_db if m.id == movie_id), None)
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    return movie.comments

@app.post("/movies/{movie_id}/comments", response_model=Movie, status_code=201)
def add_comment(
    movie_id: int,
    comment: Comment,
    user=Depends(require_permission("WRITE"))
):
    movie = next((m for m in database.movies_db if m.id == movie_id), None)
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")

    idx = database.movies_db.index(movie)
    updated = movie.dict()
    updated["comments"].append(comment.dict())
    database.movies_db[idx] = Movie(**updated)
    return database.movies_db[idx]

@app.delete("/movies/{movie_id}/comments/{comment_index}", response_model=Movie)
def delete_comment(
    movie_id: int,
    comment_index: int,
    user=Depends(require_permission("DELETE"))
):
    movie = next((m for m in database.movies_db if m.id == movie_id), None)
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")

    if comment_index < 0 or comment_index >= len(movie.comments):
        raise HTTPException(status_code=404, detail="Comment not found")

    idx = database.movies_db.index(movie)
    updated = movie.dict()
    updated["comments"].pop(comment_index)
    database.movies_db[idx] = Movie(**updated)
    return database.movies_db[idx]

@app.put("/movies/{movie_id}/comments/{comment_index}", response_model=Movie)
def edit_comment(
    movie_id: int,
    comment_index: int,
    comment: Comment,
    user=Depends(require_permission("WRITE"))
):
    movie = next((m for m in database.movies_db if m.id == movie_id), None)
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")

    if comment_index < 0 or comment_index >= len(movie.comments):
        raise HTTPException(status_code=404, detail="Comment not found")

    idx = database.movies_db.index(movie)
    updated = movie.dict()
    updated["comments"][comment_index] = comment.dict()
    database.movies_db[idx] = Movie(**updated)
    return database.movies_db[idx]