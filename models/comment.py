from pydantic import BaseModel, field_validator

class Comment(BaseModel):
    text: str
    date: str

    @field_validator('text')
    @classmethod
    def text_must_not_be_empty(cls, v):
        if not v.strip():
            raise ValueError('Comment text cannot be empty')
        if len(v) > 1000:
            raise ValueError('Comment text cannot exceed 1000 characters')
        return v.strip()

    @field_validator('date')
    @classmethod
    def date_must_not_be_empty(cls, v):
        if not v.strip():
            raise ValueError('Date cannot be empty')
        return v.strip()