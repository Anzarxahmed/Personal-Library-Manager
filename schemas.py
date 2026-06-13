from pydantic import BaseModel, Field
from typing import Optional, Dict, List

class BookCreate(BaseModel):
    title: str = Field(..., min_length=1, description="Title of the book")
    author: str = Field(..., min_length=1, description="Author of the book")
    genre: str = Field(..., min_length=1, description="Genre of the book")
    published_year: Optional[int] = Field(None, description="Year the book was published")
    reading_status: Optional[str] = Field("To Read", description="Reading status ('To Read', 'Reading', 'Completed')")
    rating: Optional[int] = Field(None, ge=1, le=5, description="Book rating from 1 to 5")
    review: Optional[str] = Field(None, description="Personal review/notes")

class BookUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1)
    author: Optional[str] = Field(None, min_length=1)
    genre: Optional[str] = Field(None, min_length=1)
    published_year: Optional[int] = None
    reading_status: Optional[str] = None
    rating: Optional[int] = Field(None, ge=1, le=5)
    review: Optional[str] = None
    summary: Optional[str] = None

class BookStats(BaseModel):
    total_books: int
    status_counts: Dict[str, int]
    genre_counts: Dict[str, int]
    average_rating: Optional[float] = None

class AIRecommendRequest(BaseModel):
    genre: str = Field(..., min_length=1, description="Genre for recommendations")

class AIRecommendItem(BaseModel):
    title: str
    author: str
    reason: str

class AIRecommendResponse(BaseModel):
    genre: str
    recommendations: List[AIRecommendItem]

class AISummaryRequest(BaseModel):
    title: str = Field(..., min_length=1, description="Title of the book to summarize")

class AISummaryResponse(BaseModel):
    title: str
    summary: str
