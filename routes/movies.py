from fastapi import APIRouter, HTTPException, Depends, Query
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from typing import Optional, List

from auth import require_permission
from database import get_db
from models import movie, comment
import db_models

security = HTTPBearer()

router = APIRouter(
    prefix="/movies",
    tags=["movies"],
    dependencies=[Depends(security)]
)

@router.get("", response_model=List[movie.Movie])
def get_movies(
    skip: int = Query(default=0, ge=0, description="Number of movies to skip"),
    limit: int = Query(default=10, ge=1, le=100, description="Max movies to return (1-100)"),
    search: Optional[str] = Query(default=None, min_length=1, max_length=100, description="Search by title"),
    genre: Optional[str] = Query(default=None, min_length=1, max_length=100, description="Filter by genre"),
    min_rating: Optional[float] = Query(default=None, ge=0, le=10, description="Minimum rating (0-10)"),
    max_rating: Optional[float] = Query(default=None, ge=0, le=10, description="Maximum rating (0-10)"),
    is_favorite: Optional[bool] = Query(default=None, description="Filter by favorite status"),
    db: Session = Depends(get_db),
    user=Depends(require_permission("READ"))
):
    if min_rating is not None and max_rating is not None and min_rating > max_rating:
        raise HTTPException(status_code=400, detail="min_rating cannot be greater than max_rating")

    query = db.query(db_models.MovieDB)

    if search:
        query = query.filter(db_models.MovieDB.title.ilike(f"%{search}%"))
    if genre:
        query = query.filter(db_models.MovieDB.genre.ilike(genre))
    if min_rating is not None:
        query = query.filter(db_models.MovieDB.rating >= min_rating)
    if max_rating is not None:
        query = query.filter(db_models.MovieDB.rating <= max_rating)
    if is_favorite is not None:
        query = query.filter(db_models.MovieDB.isFavorite == is_favorite)

    return query.offset(skip).limit(limit).all()

@router.get("/{movie_id}", response_model=movie.Movie)
def get_movie(
    movie_id: int,
    db: Session = Depends(get_db),
    user=Depends(require_permission("READ"))
):
    if movie_id <= 0:
        raise HTTPException(status_code=400, detail="Movie ID must be a positive integer")
    movie = db.query(db_models.MovieDB).filter(db_models.MovieDB.id == movie_id).first()
    if not movie:
        raise HTTPException(status_code=404, detail=f"Movie with id {movie_id} not found")
    return movie

@router.post("", response_model=movie.Movie, status_code=201)
def create_movie(
    movie: movie.MovieCreate,
    db: Session = Depends(get_db),
    user=Depends(require_permission("WRITE"))
):
    existing = db.query(db_models.MovieDB).filter(
        db_models.MovieDB.title.ilike(movie.title)
    ).first()
    if existing:
        raise HTTPException(status_code=409, detail=f"Movie '{movie.title}' already exists")

    new_movie = db_models.MovieDB(**movie.dict())
    db.add(new_movie)
    db.commit()
    db.refresh(new_movie)
    return new_movie

@router.put("/{movie_id}", response_model=movie.Movie)
def update_movie(
    movie_id: int,
    updates: movie.MovieUpdate,
    db: Session = Depends(get_db),
    user=Depends(require_permission("WRITE"))
):
    if movie_id <= 0:
        raise HTTPException(status_code=400, detail="Movie ID must be a positive integer")
    if not updates.dict(exclude_unset=True):
        raise HTTPException(status_code=400, detail="No fields provided to update")

    movie = db.query(db_models.MovieDB).filter(db_models.MovieDB.id == movie_id).first()
    if not movie:
        raise HTTPException(status_code=404, detail=f"Movie with id {movie_id} not found")

    for key, value in updates.dict(exclude_unset=True).items():
        setattr(movie, key, value)

    db.commit()
    db.refresh(movie)
    return movie

@router.delete("/{movie_id}", status_code=204)
def delete_movie(
    movie_id: int,
    db: Session = Depends(get_db),
    user=Depends(require_permission("DELETE"))
):
    if movie_id <= 0:
        raise HTTPException(status_code=400, detail="Movie ID must be a positive integer")
    movie = db.query(db_models.MovieDB).filter(db_models.MovieDB.id == movie_id).first()
    if not movie:
        raise HTTPException(status_code=404, detail=f"Movie with id {movie_id} not found")
    db.delete(movie)
    db.commit()
    return None