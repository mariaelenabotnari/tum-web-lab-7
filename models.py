from pydantic import BaseModel
from typing import Optional, List

class Comment(BaseModel):
    text: str
    date: str

class Movie(BaseModel):
    id: int
    title: str
    rating: Optional[float] = None
    genre: str
    year: str
    image: str
    isFavorite: bool = False
    comments: List[Comment] = []

    class Config:
        from_attributes = True

class MovieCreate(BaseModel):
    title: str
    rating: Optional[float] = None
    genre: str
    year: str
    image: str
    isFavorite: bool = False
    comments: List[Comment] = []

class MovieUpdate(BaseModel):
    title: Optional[str] = None
    rating: Optional[float] = None
    genre: Optional[str] = None
    year: Optional[str] = None
    image: Optional[str] = None
    isFavorite: Optional[bool] = None
    comments: Optional[List[Comment]] = None