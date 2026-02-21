"""
사용자 데이터베이스 모델
SQLAlchemy ORM
"""

from sqlalchemy import Column, String, DateTime, Boolean, Integer
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from passlib.context import CryptContext

Base = declarative_base()

# 비밀번호 해싱
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=12
)


class User(Base):
    """사용자 모델"""
    
    __tablename__ = "users"
    
    # 기본 정보
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    
    # 프로필
    full_name = Column(String(100), nullable=True)
    phone_number = Column(String(20), nullable=True)
    
    # 상태
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    
    # 투자 프로필
    risk_profile = Column(String(20), default="중립")  # 보수, 중립, 공격
    account_size = Column(Integer, default=0)  # 계좌 규모 (원)
    investment_period = Column(String(20), default="단기")  # 단기, 중기, 장기
    
    # 타임스탬프
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)
    
    def set_password(self, password: str):
        """비밀번호 해싱하여 저장"""
        self.hashed_password = pwd_context.hash(password)
    
    def verify_password(self, password: str) -> bool:
        """비밀번호 검증"""
        return pwd_context.verify(password, self.hashed_password)
    
    def __repr__(self) -> str:
        return f"<User {self.username} ({self.email})>"


class UserSession(Base):
    """사용자 세션 (토큰 관리)"""
    
    __tablename__ = "user_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True, nullable=False)
    token = Column(String(500), unique=True, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)
    
    def is_expired(self) -> bool:
        """토큰 만료 여부"""
        return datetime.utcnow() > self.expires_at
    
    def __repr__(self) -> str:
        return f"<UserSession user_id={self.user_id}>"
