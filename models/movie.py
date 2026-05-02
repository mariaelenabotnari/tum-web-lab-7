from pydantic import BaseModel, field_validator
from typing import Optional, List
from models.comment import Comment

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

    @field_validator('title')
    @classmethod
    def title_must_not_be_empty(cls, v):
        if not v.strip():
            raise ValueError('Title cannot be empty')
        if len(v) > 200:
            raise ValueError('Title cannot exceed 200 characters')
        return v.strip()

    @field_validator('rating')
    @classmethod
    def rating_must_be_valid(cls, v):
        if v is not None and (v < 0 or v > 10):
            raise ValueError('Rating must be between 0 and 10')
        return v

    @field_validator('genre')
    @classmethod
    def genre_must_not_be_empty(cls, v):
        if not v.strip():
            raise ValueError('Genre cannot be empty')
        if len(v) > 100:
            raise ValueError('Genre cannot exceed 100 characters')
        return v.strip()

    @field_validator('year')
    @classmethod
    def year_must_be_valid(cls, v):
        if not v.strip():
            raise ValueError('Year cannot be empty')
        try:
            year_int = int(v.strip())
            if year_int < 1888 or year_int > 2100:
                raise ValueError('Year must be between 1888 and 2100')
        except ValueError as e:
            if 'between' in str(e):
                raise
            raise ValueError('Year must be a valid number')
        return v.strip()

    @field_validator('image')
    @classmethod
    def image_must_not_be_empty(cls, v):
        if not v.strip():
            raise ValueError('Image URL cannot be empty')
        return v.strip()

class MovieUpdate(BaseModel):
    title: Optional[str] = None
    rating: Optional[float] = None
    genre: Optional[str] = None
    year: Optional[str] = None
    image: Optional[str] = None
    isFavorite: Optional[bool] = None
    comments: Optional[List[Comment]] = None

    @field_validator('title')
    @classmethod
    def title_must_not_be_empty(cls, v):
        if v is not None and not v.strip():
            raise ValueError('Title cannot be empty')
        if v is not None and len(v) > 200:
            raise ValueError('Title cannot exceed 200 characters')
        return v

    @field_validator('rating')
    @classmethod
    def rating_must_be_valid(cls, v):
        if v is not None and (v < 0 or v > 10):
            raise ValueError('Rating must be between 0 and 10')
        return v

    @field_validator('year')
    @classmethod
    def year_must_be_valid(cls, v):
        if v is not None:
            try:
                year_int = int(v.strip())
                if year_int < 1888 or year_int > 2100:
                    raise ValueError('Year must be between 1888 and 2100')
            except ValueError as e:
                if 'between' in str(e):
                    raise
                raise ValueError('Year must be a valid number')
        return v