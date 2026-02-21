"""
FastAPI 인증 미들웨어 및 의존성
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthCredentials
from sqlalchemy.orm import Session
from typing import Optional

from services.jwt_service import JWTService
from services.user_service import UserService, SessionService
from models.user import User
from database import get_db as _get_db


# HTTP Bearer 보안 스킴
security = HTTPBearer()


async def get_db() -> Session:
    """
    데이터베이스 세션 의존성
    """
    async for db in _get_db():
        yield db


async def get_current_user(
    credentials: HTTPAuthCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    현재 사용자 가져오기 (인증 필수)
    
    사용 방법:
        @app.get("/api/profile")
        async def get_profile(user: User = Depends(get_current_user)):
            ...
    """
    token = credentials.credentials
    
    # 토큰 검증
    user_id = JWTService.verify_token(token)
    
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="토큰이 유효하지 않습니다"
        )
    
    # 사용자 조회
    user = UserService.get_user_by_id(db, user_id)
    
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="사용자를 찾을 수 없습니다"
        )
    
    return user


async def get_current_user_optional(
    credentials: Optional[HTTPAuthCredentials] = Depends(security),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """
    현재 사용자 가져오기 (선택사항)
    
    사용 방법:
        @app.get("/api/recommendations")
        async def get_recommendations(user: Optional[User] = Depends(get_current_user_optional)):
            if user:
                # 인증된 사용자
                ...
    """
    if credentials is None:
        return None
    
    token = credentials.credentials
    
    # 토큰 검증
    user_id = JWTService.verify_token(token)
    
    if user_id is None:
        return None
    
    # 사용자 조회
    user = UserService.get_user_by_id(db, user_id)
    
    if not user or not user.is_active:
        return None
    
    return user
