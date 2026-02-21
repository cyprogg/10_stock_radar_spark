"""
JWT 토큰 생성 및 검증
"""

import jwt
import os
from datetime import datetime, timedelta
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

# JWT 설정
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production-2026-spring")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "1440"))  # 24시간


class JWTService:
    """JWT 토큰 서비스"""
    
    @staticmethod
    def create_access_token(user_id: int, expires_delta: Optional[timedelta] = None) -> tuple[str, datetime]:
        """
        액세스 토큰 생성
        
        Args:
            user_id: 사용자 ID
            expires_delta: 만료 시간 (기본값: 24시간)
            
        Returns:
            (token, expire_datetime) 튜플
        """
        if expires_delta is None:
            expires_delta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
        expire = datetime.utcnow() + expires_delta
        
        payload = {
            "sub": user_id,
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "access"
        }
        
        token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
        return token, expire
    
    @staticmethod
    def create_refresh_token(user_id: int) -> str:
        """
        리프레시 토큰 생성
        
        Args:
            user_id: 사용자 ID
            
        Returns:
            refresh token
        """
        expire = datetime.utcnow() + timedelta(days=7)  # 7일
        
        payload = {
            "sub": user_id,
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "refresh"
        }
        
        token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
        return token
    
    @staticmethod
    def verify_token(token: str) -> Optional[int]:
        """
        토큰 검증 및 user_id 추출
        
        Args:
            token: JWT 토큰
            
        Returns:
            user_id 또는 None (검증 실패)
        """
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            
            # 토큰 타입 확인
            if payload.get("type") != "access":
                return None
            
            user_id: int = payload.get("sub")
            
            if user_id is None:
                return None
            
            return user_id
        
        except jwt.ExpiredSignatureError:
            # 토큰 만료
            return None
        except jwt.InvalidTokenError:
            # 토큰 검증 실패
            return None
    
    @staticmethod
    def get_user_id_from_token(token: str) -> Optional[int]:
        """토큰에서 user_id 추출"""
        try:
            # "Bearer " 제거
            if token.startswith("Bearer "):
                token = token[7:]
            
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload.get("sub")
        except:
            return None
    
    @staticmethod
    def decode_token(token: str) -> Optional[dict]:
        """토큰 디코드 (검증 포함)"""
        try:
            # "Bearer " 제거
            if token.startswith("Bearer "):
                token = token[7:]
            
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload
        except:
            return None
