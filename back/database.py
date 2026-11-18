"""
SQLite 데이터베이스 연결 및 SQLAlchemy 세션을 관리합니다.
"""

from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker


# 데이터베이스 파일 경로 설정
DATABASE_PATH = Path(__file__).resolve().parent / "movies.db"
DATABASE_URL = f"sqlite:///{DATABASE_PATH}"

# SQLite 데이터베이스 엔진 생성
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
)

# 데이터베이스 세션 설정
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

# ORM 모델의 기본 클래스 정의
Base = declarative_base()

# 요청별 데이터베이스 세션을 생성하고 종료
def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()