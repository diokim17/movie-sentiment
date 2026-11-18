"""
영화 및 리뷰 서비스를 위한 FastAPI 애플리케이션을 실행합니다.
"""

from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy.orm import Session

from .database import Base, engine, get_db
from .models import Movie, Review
from .schemas import MovieCreate, MovieResponse, ReviewCreate, ReviewResponse
from .sentiment import analyze_sentiment


# FastAPI 애플리케이션 생성
app = FastAPI(
    title="Movie Review API",
    description="영화 정보, 사용자 리뷰 및 감성 분석을 제공하는 API",
    version="1.0.0",
)

# 데이터베이스 테이블 생성
Base.metadata.create_all(bind=engine)

# 전체 영화 목록 조회
@app.get(
    "/movies",
    response_model=list[MovieResponse],
    summary="전체 영화 조회",
    tags=["Movies"],
)

def get_movies(db: Session = Depends(get_db)):
    return db.query(Movie).all()

# 특정 영화의 상세 정보를 조회
@app.get(
    "/movies/{movie_id}",
    response_model=MovieResponse,
    summary="특정 영화 조회",
    tags=["Movies"],
)

def get_movie(movie_id: int, db: Session = Depends(get_db)):
    movie = db.get(Movie, movie_id)

    if movie is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="영화를 찾을 수 없습니다.",
        )

    return movie

# 새로운 영화를 등록
@app.post(
    "/movies",
    response_model=MovieResponse,
    status_code=status.HTTP_201_CREATED,
    summary="영화 등록",
    tags=["Movies"],
)

def create_movie(
    movie_data: MovieCreate,
    db: Session = Depends(get_db),
):
    movie = Movie(
        **movie_data.model_dump(
            mode="python",
            exclude={"poster_url"},
        ),
        poster_url = str(movie_data.poster_url),
    )

    db.add(movie)
    db.commit()
    db.refresh(movie)

    return movie

# 특정 영화를 삭제
@app.delete(
    "/movies/{movie_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="영화 삭제",
    tags=["Movies"],
)

def delete_movie(movie_id: int, db: Session = Depends(get_db)):
    movie = db.get(Movie, movie_id)

    if movie is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="영화를 찾을 수 없습니다.",
        )

    db.delete(movie)
    db.commit()

# 특정 영화의 전체 리뷰 조회
@app.get(
    "/movies/{movie_id}/reviews",
    response_model=list[ReviewResponse],
    summary="영화별 리뷰 조회",
    description="영화 ID를 기준으로 등록된 리뷰와 감성 분석 결과를 조회합니다.",
    tags=["Reviews"],
)

def get_reviews(movie_id: int, db: Session = Depends(get_db)):
    movie = db.get(Movie, movie_id)

    if movie is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="영화를 찾을 수 없습니다.",
        )

    return db.query(Review).filter(Review.movie_id == movie_id).all()


# 영화 리뷰를 등록하고 GPT API로 감성을 분석
@app.post(
    "/movies/{movie_id}/reviews",
    response_model=ReviewResponse,
    status_code=status.HTTP_201_CREATED,
    summary="영화 리뷰 등록 및 감성 분석",
    description="리뷰를 등록하면 GPT API가 긍정, 부정, 중립으로 감성을 분석하고 결과를 저장합니다.",
    tags=["Reviews"],
)
def create_review(
    movie_id: int,
    review_data: ReviewCreate,
    db: Session = Depends(get_db),
):
    movie = db.get(Movie, movie_id)

    if movie is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="영화를 찾을 수 없습니다.",
        )

    try:
        result = analyze_sentiment(review_data.content)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="감성 분석 API 호출에 실패했습니다.",
        ) from None

    review = Review(
        movie_id=movie_id,
        content=review_data.content,
        rating=review_data.rating,
        sentiment=result.sentiment,
        sentiment_reason=result.reason,
    )

    db.add(review)
    db.commit()
    db.refresh(review)

    return review
