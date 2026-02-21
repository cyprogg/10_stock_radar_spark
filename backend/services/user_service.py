"""
사용자 관리 서비스
"""

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import Optional, Tuple
from datetime import datetime, timedelta
import re

from models.user import User, UserSession
from schemas.auth import UserResponse
from services.jwt_service import JWTService


class UserService:
    """사용자 관리 서비스"""
    
    @staticmethod
    def register_user(
        db: Session,
        username: str,
        email: str,
        password: str,
        full_name: Optional[str] = None,
        phone_number: Optional[str] = None
    ) -> Tuple[bool, str, Optional[User]]:
        """
        사용자 등록
        
        Returns:
            (성공 여부, 메시지, 사용자 객체)
        """
        # 중복 체크
        existing_user = db.query(User).filter(
            (User.username == username) | (User.email == email)
        ).first()
        
        if existing_user:
            if existing_user.username == username:
                return False, "이미 존재하는 사용자명입니다", None
            else:
                return False, "이미 등록된 이메일입니다", None
        
        # 새 사용자 생성
        new_user = User(
            username=username,
            email=email,
            full_name=full_name,
            phone_number=phone_number
        )
        new_user.set_password(password)
        
        try:
            db.add(new_user)
            db.commit()
            db.refresh(new_user)
            return True, "회원가입 성공", new_user
        except IntegrityError:
            db.rollback()
            return False, "데이터베이스 오류가 발생했습니다", None
        except Exception as e:
            db.rollback()
            return False, f"오류 발생: {str(e)}", None
    
    @staticmethod
    def login(
        db: Session,
        username: str,
        password: str
    ) -> Tuple[bool, str, Optional[User]]:
        """
        사용자 로그인
        
        Returns:
            (성공 여부, 메시지, 사용자 객체)
        """
        # 사용자 조회
        user = db.query(User).filter(User.username == username).first()
        
        if not user:
            return False, "사용자를 찾을 수 없습니다", None
        
        if not user.is_active:
            return False, "비활성화된 계정입니다", None
        
        # 비밀번호 검증
        if not user.verify_password(password):
            return False, "비밀번호가 올바르지 않습니다", None
        
        # 마지막 로그인 시간 업데이트
        user.last_login = datetime.utcnow()
        db.commit()
        
        return True, "로그인 성공", user
    
    @staticmethod
    def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
        """ID로 사용자 조회"""
        return db.query(User).filter(User.id == user_id).first()
    
    @staticmethod
    def get_user_by_username(db: Session, username: str) -> Optional[User]:
        """사용자명으로 사용자 조회"""
        return db.query(User).filter(User.username == username).first()
    
    @staticmethod
    def update_user_profile(
        db: Session,
        user_id: int,
        **kwargs
    ) -> Tuple[bool, str, Optional[User]]:
        """
        사용자 프로필 업데이트
        
        Args:
            user_id: 사용자 ID
            **kwargs: 업데이트할 필드들
        """
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            return False, "사용자를 찾을 수 없습니다", None
        
        # 허용된 필드만 업데이트
        allowed_fields = [
            "full_name", "phone_number", "risk_profile",
            "account_size", "investment_period"
        ]
        
        for field, value in kwargs.items():
            if field in allowed_fields and value is not None:
                setattr(user, field, value)
        
        try:
            user.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(user)
            return True, "프로필 업데이트 성공", user
        except Exception as e:
            db.rollback()
            return False, f"오류 발생: {str(e)}", None
    
    @staticmethod
    def change_password(
        db: Session,
        user_id: int,
        old_password: str,
        new_password: str
    ) -> Tuple[bool, str]:
        """
        비밀번호 변경
        
        Returns:
            (성공 여부, 메시지)
        """
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            return False, "사용자를 찾을 수 없습니다"
        
        # 기존 비밀번호 검증
        if not user.verify_password(old_password):
            return False, "현재 비밀번호가 올바르지 않습니다"
        
        # 새 비밀번호 설정
        user.set_password(new_password)
        user.updated_at = datetime.utcnow()
        
        try:
            db.commit()
            return True, "비밀번호 변경 성공"
        except Exception as e:
            db.rollback()
            return False, f"오류 발생: {str(e)}"
    
    @staticmethod
    def deactivate_user(db: Session, user_id: int) -> Tuple[bool, str]:
        """
        계정 비활성화
        
        Returns:
            (성공 여부, 메시지)
        """
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            return False, "사용자를 찾을 수 없습니다"
        
        user.is_active = False
        user.updated_at = datetime.utcnow()
        
        try:
            db.commit()
            return True, "계정이 비활성화되었습니다"
        except Exception as e:
            db.rollback()
            return False, f"오류 발생: {str(e)}"


class SessionService:
    """사용자 세션 관리"""
    
    @staticmethod
    def create_session(
        db: Session,
        user_id: int,
        token: str,
        expires_at: datetime
    ) -> bool:
        """세션 생성"""
        session = UserSession(
            user_id=user_id,
            token=token,
            expires_at=expires_at
        )
        
        try:
            db.add(session)
            db.commit()
            return True
        except:
            db.rollback()
            return False
    
    @staticmethod
    def get_session(db: Session, token: str) -> Optional[UserSession]:
        """토큰으로 세션 조회"""
        return db.query(UserSession).filter(
            UserSession.token == token,
            UserSession.is_active == True
        ).first()
    
    @staticmethod
    def invalidate_session(db: Session, token: str) -> bool:
        """세션 무효화 (로그아웃)"""
        session = db.query(UserSession).filter(UserSession.token == token).first()
        
        if not session:
            return False
        
        session.is_active = False
        
        try:
            db.commit()
            return True
        except:
            db.rollback()
            return False
    
    @staticmethod
    def cleanup_expired_sessions(db: Session) -> int:
        """만료된 세션 정리"""
        try:
            result = db.query(UserSession).filter(
                UserSession.expires_at < datetime.utcnow()
            ).delete()
            db.commit()
            return result
        except:
            db.rollback()
            return 0
