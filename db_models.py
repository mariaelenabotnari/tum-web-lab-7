from sqlalchemy import Column, Integer, String, Float, Boolean, JSON
from database import Base

class MovieDB(Base):
    __tablename__ = "movies"

    id       = Column(Integer, primary_key=True, index=True)
    title    = Column(String, nullable=False)
    rating   = Column(Float, nullable=True)
    genre    = Column(String, nullable=False)
    year     = Column(String, nullable=False)
    image    = Column(String, nullable=False)
    isFavorite = Column(Boolean, default=False)
    comments = Column(JSON, default=[])