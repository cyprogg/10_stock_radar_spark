"""
인증 API 엔드포인트
FastAPI 라우터
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta

from schemas.auth import (
    UserRegisterRequest, UserLoginRequest, TokenResponse,
    UserResponse, UserProfileUpdate, PasswordChangeRequest,
    AuthResponse
)
from models.user import User
from services.user_service import UserService, SessionService
from services.jwt_service import JWTService
from dependencies.auth import get_current_user, get_db

# 라우터 생성
router = APIRouter(prefix="/api/auth", tags=["authentication"])


@router.post("/signup", response_model=AuthResponse)
async def signup(
    request: UserRegisterRequest,
    db: Session = Depends(get_db)
):
    """
    회원가입
    
    Request Body:
    - username: 사용자명 (3-50자)
    - email: 이메일
    - password: 비밀번호 (8자 이상, 대문자+숫자 포함)
    - password_confirm: 비밀번호 확인
    - full_name: 전체 이름 (선택)
    - phone_number: 전화번호 (선택)
    """
    success, message, user = UserService.register_user(
        db,
        username=request.username,
        email=request.email,
        password=request.password,
        full_name=request.full_name,
        phone_number=request.phone_number
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message
        )
    
    return AuthResponse(
        success=True,
        message=message,
        data={"user_id": user.id, "username": user.username}
    )


@router.post("/login", response_model=TokenResponse)
async def login(
    request: UserLoginRequest,
    db: Session = Depends(get_db)
):
    """
    로그인
    
    Request Body:
    - username: 사용자명
    - password: 비밀번호
    
    Response: JWT 토큰 + 사용자 정보
    """
    success, message, user = UserService.login(
        db,
        username=request.username,
        password=request.password
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=message
        )
    
    # 액세스 토큰 생성
    token, expires_at = JWTService.create_access_token(user.id)
    
    # 세션 저장 (선택)
    SessionService.create_session(db, user.id, token, expires_at)
    
    return TokenResponse(
        access_token=token,
        token_type="bearer",
        expires_in=24 * 60 * 60,  # 24시간 (초 단위)
        user=UserResponse.from_orm(user)
    )


@router.post("/logout", response_model=AuthResponse)
async def logout(
    user: User = Depends(get_current_user),
    credentials = None,  # HTTP Bearer 토큰
    db: Session = Depends(get_db)
):
    """
    로그아웃
    
    Header:
    - Authorization: Bearer <token>
    """
    # 세션 무효화 (optional)
    # SessionService.invalidate_session(db, token)
    
    return AuthResponse(
        success=True,
        message="로그아웃 성공"
    )


@router.get("/me", response_model=AuthResponse)
async def get_me(
    user: User = Depends(get_current_user)
):
    """
    현재 사용자 정보 조회
    
    Header:
    - Authorization: Bearer <token>
    """
    return AuthResponse(
        success=True,
        message="사용자 정보 조회 성공",
        data={
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "full_name": user.full_name,
            "risk_profile": user.risk_profile,
            "investment_period": user.investment_period,
            "account_size": user.account_size,
            "is_active": user.is_active,
            "created_at": user.created_at.isoformat() if user.created_at else None,
            "last_login": user.last_login.isoformat() if user.last_login else None
        }
    )


@router.put("/profile", response_model=AuthResponse)
async def update_profile(
    request: UserProfileUpdate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    프로필 업데이트
    
    Header:
    - Authorization: Bearer <token>
    
    Request Body:
    - full_name: 전체 이름
    - phone_number: 전화번호
    - risk_profile: 투자 성향 (보수/중립/공격)
    - account_size: 계좌 규모
    - investment_period: 투자 기간 (단기/중기/장기)
    """
    success, message, updated_user = UserService.update_user_profile(
        db,
        user.id,
        **request.dict(exclude_unset=True)
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message
        )
    
    return AuthResponse(
        success=True,
        message=message,
        data=UserResponse.from_orm(updated_user).dict()
    )


@router.post("/change-password", response_model=AuthResponse)
async def change_password(
    request: PasswordChangeRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    비밀번호 변경
    
    Header:
    - Authorization: Bearer <token>
    
    Request Body:
    - old_password: 현재 비밀번호
    - new_password: 새 비밀번호
    - new_password_confirm: 새 비밀번호 확인
    """
    success, message = UserService.change_password(
        db,
        user.id,
        request.old_password,
        request.new_password
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message
        )
    
    return AuthResponse(success=True, message=message)


@router.post("/deactivate", response_model=AuthResponse)
async def deactivate_account(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    계정 비활성화 (삭제 아님)
    
    Header:
    - Authorization: Bearer <token>
    """
    success, message = UserService.deactivate_user(db, user.id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message
        )
    
    return AuthResponse(success=True, message=message)


# 헬스 체크
@router.get("/health")
async def health_check():
    """인증 서비스 헬스 체크"""
    return {"status": "ok", "service": "authentication"}
