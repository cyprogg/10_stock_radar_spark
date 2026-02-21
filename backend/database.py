"""
SQLAlchemy 데이터베이스 설정
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
import os
from dotenv import load_dotenv

load_dotenv()

# 데이터베이스 URL
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./stock_radar.db?timeout=30&check_same_thread=False"
)

# SQLite인지 확인
if DATABASE_URL.startswith("sqlite"):
    # SQLite 설정 (개발용)
    engine = create_engine(
        DATABASE_URL,
        connect_args={"timeout": 30, "check_same_thread": False},
        poolclass=StaticPool,
        echo=False
    )
else:
    # PostgreSQL 설정 (프로덕션)
    engine = create_engine(
        DATABASE_URL,
        pool_size=10,
        max_overflow=20,
        pool_recycle=3600,
        echo=False
    )

# 세션 팩토리
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


def get_db() -> Session:
    """데이터베이스 세션 제공"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """데이터베이스 초기화 (테이블 생성)"""
    from models.user import Base
    
    Base.metadata.create_all(bind=engine)
    print("✅ 데이터베이스 초기화 완료")


if __name__ == "__main__":
    init_db()
