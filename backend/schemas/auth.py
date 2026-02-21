"""
Pydantic 스키마 - 데이터 검증
"""

from pydantic import BaseModel, EmailStr, Field, validator
from datetime import datetime
from typing import Optional


class UserRegisterRequest(BaseModel):
    """회원가입 요청"""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8)
    password_confirm: str
    full_name: Optional[str] = None
    phone_number: Optional[str] = None
    
    @validator("password_confirm")
    def passwords_match(cls, v, values):
        if "password" in values and v != values["password"]:
            raise ValueError("비밀번호가 일치하지 않습니다")
        return v
    
    @validator("password")
    def password_complexity(cls, v):
        """비밀번호 복잡도 검증"""
        if not any(char.isupper() for char in v):
            raise ValueError("대문자를 포함해야 합니다")
        if not any(char.isdigit() for char in v):
            raise ValueError("숫자를 포함해야 합니다")
        return v


class UserLoginRequest(BaseModel):
    """로그인 요청"""
    username: str
    password: str


class UserResponse(BaseModel):
    """사용자 정보 응답"""
    id: int
    username: str
    email: str
    full_name: Optional[str]
    is_active: bool
    risk_profile: str
    account_size: int
    investment_period: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class UserProfileUpdate(BaseModel):
    """사용자 프로필 업데이트"""
    full_name: Optional[str] = None
    phone_number: Optional[str] = None
    risk_profile: Optional[str] = None
    account_size: Optional[int] = None
    investment_period: Optional[str] = None


class PasswordChangeRequest(BaseModel):
    """비밀번호 변경"""
    old_password: str
    new_password: str = Field(..., min_length=8)
    new_password_confirm: str
    
    @validator("new_password_confirm")
    def passwords_match(cls, v, values):
        if "new_password" in values and v != values["new_password"]:
            raise ValueError("새 비밀번호가 일치하지 않습니다")
        return v


class TokenResponse(BaseModel):
    """토큰 응답"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse


class TokenPayload(BaseModel):
    """JWT 토큰 페이로드"""
    sub: int  # user_id
    exp: float  # 만료 시간 (Unix timestamp)
    iat: float  # 발급 시간 (Unix timestamp)


class ErrorResponse(BaseModel):
    """에러 응답"""
    detail: str
    code: str


class AuthResponse(BaseModel):
    """일반 응답"""
    success: bool
    message: str
    data: Optional[dict] = None
