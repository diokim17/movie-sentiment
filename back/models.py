"""
영화 및 리뷰 데이터를 관리하는 SQLAlchemy ORM 모델을 정의합니다.
"""

from datetime import date, datetime, timezone

from sqlalchemy import Date, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


# 영화 정보를 저장하는 ORM 모델
class Movie(Base):
    __tablename__ = "movies"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    release_date: Mapped[date] = mapped_column(Date, nullable=False)
    director: Mapped[str] = mapped_column(String(100), nullable=False)
    genre: Mapped[str] = mapped_column(String(100), nullable=False)
    poster_url: Mapped[str] = mapped_column(String(500), nullable=False)
    reviews: Mapped[list["Review"]] = relationship(
        back_populates="movie",
        cascade="all, delete-orphan",
    )

# 영화 리뷰와 감성 분석 결과를 저장하는 ORM 모델
class Review(Base):
    __tablename__ = "reviews"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    movie_id: Mapped[int] = mapped_column(
        ForeignKey("movies.id"),
        nullable=False,
    )
    content: Mapped[str] = mapped_column(Text, nullable=False)
    rating: Mapped[float] = mapped_column(Float, nullable=False)
    sentiment: Mapped[str] = mapped_column(String(20), nullable=False)
    sentiment_reason: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    movie: Mapped["Movie"] = relationship(back_populates="reviews")