from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import Optional, List

from auth import require_permission
from database import get_db
from models import Movie, MovieCreate, MovieUpdate, Comment
import db_models

router = APIRouter(prefix="/movies", tags=["movies"])

@router.get("", response_model=List[Movie])
def get_movies(
    skip: int = 0,
    limit: int = 10,
    search: Optional[str] = None,
    genre: Optional[str] = None,
    min_rating: Optional[float] = None,
    max_rating: Optional[float] = None,
    is_favorite: Optional[bool] = None,
    db: Session = Depends(get_db),
    user=Depends(require_permission("READ"))
):
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

@router.get("/{movie_id}", response_model=Movie)
def get_movie(
    movie_id: int,
    db: Session = Depends(get_db),
    user=Depends(require_permission("READ"))
):
    movie = db.query(db_models.MovieDB).filter(db_models.MovieDB.id == movie_id).first()
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    return movie

@router.post("", response_model=Movie, status_code=201)
def create_movie(
    movie: MovieCreate,
    db: Session = Depends(get_db),
    user=Depends(require_permission("WRITE"))
):
    new_movie = db_models.MovieDB(**movie.dict())
    db.add(new_movie)
    db.commit()
    db.refresh(new_movie)
    return new_movie

@router.put("/{movie_id}", response_model=Movie)
def update_movie(
    movie_id: int,
    updates: MovieUpdate,
    db: Session = Depends(get_db),
    user=Depends(require_permission("WRITE"))
):
    movie = db.query(db_models.MovieDB).filter(db_models.MovieDB.id == movie_id).first()
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")
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
    movie = db.query(db_models.MovieDB).filter(db_models.MovieDB.id == movie_id).first()
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    db.delete(movie)
    db.commit()
    return None

@router.get("/{movie_id}/comments", response_model=List[Comment])
def get_comments(
    movie_id: int,
    db: Session = Depends(get_db),
    user=Depends(require_permission("READ"))
):
    movie = db.query(db_models.MovieDB).filter(db_models.MovieDB.id == movie_id).first()
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    return movie.comments or []

@router.post("/{movie_id}/comments", response_model=Movie, status_code=201)
def add_comment(
    movie_id: int,
    comment: Comment,
    db: Session = Depends(get_db),
    user=Depends(require_permission("WRITE"))
):
    movie = db.query(db_models.MovieDB).filter(db_models.MovieDB.id == movie_id).first()
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    comments = list(movie.comments or [])
    comments.append(comment.dict())
    movie.comments = comments
    db.commit()
    db.refresh(movie)
    return movie

@router.delete("/{movie_id}/comments/{comment_index}", response_model=Movie)
def delete_comment(
    movie_id: int,
    comment_index: int,
    db: Session = Depends(get_db),
    user=Depends(require_permission("DELETE"))
):
    movie = db.query(db_models.MovieDB).filter(db_models.MovieDB.id == movie_id).first()
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    comments = list(movie.comments or [])
    if comment_index < 0 or comment_index >= len(comments):
        raise HTTPException(status_code=404, detail="Comment not found")
    comments.pop(comment_index)
    movie.comments = comments
    db.commit()
    db.refresh(movie)
    return movie

@router.put("/{movie_id}/comments/{comment_index}", response_model=Movie)
def edit_comment(
    movie_id: int,
    comment_index: int,
    comment: Comment,
    db: Session = Depends(get_db),
    user=Depends(require_permission("WRITE"))
):
    movie = db.query(db_models.MovieDB).filter(db_models.MovieDB.id == movie_id).first()
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    comments = list(movie.comments or [])
    if comment_index < 0 or comment_index >= len(comments):
        raise HTTPException(status_code=404, detail="Comment not found")
    comments[comment_index] = comment.dict()
    movie.comments = comments
    db.commit()
    db.refresh(movie)
    return movie