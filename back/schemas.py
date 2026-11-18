"""
영화 및 리뷰 API의 요청과 응답 데이터 스키마를 정의합니다.
"""

from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, HttpUrl


# 영화 등록 요청 데이터 검증
class MovieCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    release_date: date
    director: str = Field(min_length=1, max_length=100)
    genre: str = Field(min_length=1, max_length=100)
    poster_url: HttpUrl

# 영화 조회 응답 데이터를 정의
class MovieResponse(MovieCreate):
    id: int

    model_config = ConfigDict(from_attributes=True)

# 리뷰 등록 요청 데이터 검증
class ReviewCreate(BaseModel):
    content: str = Field(min_length=1)
    rating: float = Field(ge=0, le=5)

# 리뷰 조회 응답 데이터를 정의
class ReviewResponse(ReviewCreate):
    id: int
    movie_id: int
    sentiment: Literal["positive", "negative", "neutral"]
    sentiment_reason: str
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)