from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from typing import List

from auth import require_permission
from database import get_db
from models import comment, movie

import db_models

security = HTTPBearer()

router = APIRouter(
    prefix="/movies",
    tags=["comments"],
    dependencies=[Depends(security)]
)

@router.get("/{movie_id}/comments", response_model=List[comment.Comment])
def get_comments(
    movie_id: int,
    db: Session = Depends(get_db),
    user=Depends(require_permission("READ"))
):
    movie = db.query(db_models.MovieDB).filter(db_models.MovieDB.id == movie_id).first()
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    return movie.comments or []

@router.post("/{movie_id}/comments", response_model=movie.Movie, status_code=201)
def add_comment(
    movie_id: int,
    comment: comment.Comment,
    db: Session = Depends(get_db),
    user=Depends(require_permission("WRITE"))
):
    movie = db.query(db_models.MovieDB).filter(db_models.MovieDB.id == movie_id).first()
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    comments = list(movie.comments or [])
    if len(comments) >= 100:
        raise HTTPException(status_code=400, detail="Movie cannot have more than 100 comments")
    comments.append(comment.dict())
    movie.comments = comments
    db.commit()
    db.refresh(movie)
    return movie

@router.delete("/{movie_id}/comments/{comment_index}", response_model=movie.Movie)
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
        raise HTTPException(status_code=404, detail=f"Comment index {comment_index} not found. Movie has {len(comments)} comments")
    comments.pop(comment_index)
    movie.comments = comments
    db.commit()
    db.refresh(movie)
    return movie

@router.put("/{movie_id}/comments/{comment_index}", response_model=movie.Movie)
def edit_comment(
    movie_id: int,
    comment_index: int,
    comment: comment.Comment,
    db: Session = Depends(get_db),
    user=Depends(require_permission("WRITE"))
):
    movie = db.query(db_models.MovieDB).filter(db_models.MovieDB.id == movie_id).first()
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    comments = list(movie.comments or [])
    if comment_index < 0 or comment_index >= len(comments):
        raise HTTPException(status_code=404, detail=f"Comment index {comment_index} not found. Movie has {len(comments)} comments")
    comments[comment_index] = comment.dict()
    movie.comments = comments
    db.commit()
    db.refresh(movie)
    return movie