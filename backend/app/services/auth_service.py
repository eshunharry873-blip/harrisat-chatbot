from sqlalchemy.orm import Session
from app.models import User
from app.schemas import UserCreate, UserLogin, Token
from app.utils import hash_password, verify_password, create_access_token, create_refresh_token
from app.logger import logger
from fastapi import HTTPException, status
from datetime import datetime

class AuthService:
    @staticmethod
    def register_user(db: Session, user_create: UserCreate) -> User:
        existing_user = db.query(User).filter(
            (User.email == user_create.email) | (User.username == user_create.username)
        ).first()
        
        if existing_user:
            logger.warning(f"Registration attempt with existing email/username: {user_create.email}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email or username already registered"
            )
        
        hashed_password = hash_password(user_create.password)
        db_user = User(
            email=user_create.email,
            username=user_create.username,
            full_name=user_create.full_name,
            hashed_password=hashed_password
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        logger.info(f"User registered: {user_create.email}")
        return db_user
    
    @staticmethod
    def login_user(db: Session, user_login: UserLogin) -> Token:
        user = db.query(User).filter(User.email == user_login.email).first()
        
        if not user or not verify_password(user_login.password, user.hashed_password):
            logger.warning(f"Failed login attempt: {user_login.email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is inactive"
            )
        
        user.last_login = datetime.utcnow()
        db.commit()
        
        access_token = create_access_token(data={"sub": user.id})
        refresh_token = create_refresh_token(data={"sub": user.id})
        
        logger.info(f"User logged in: {user.email}")
        return Token(access_token=access_token, refresh_token=refresh_token)
    
    @staticmethod
    def refresh_access_token(refresh_token: str) -> Token:
        try:
            import jwt
            from app.config import settings
            payload = jwt.decode(refresh_token, settings.secret_key, algorithms=[settings.algorithm])
            user_id = payload.get("sub")
            if not user_id:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid refresh token"
                )
            access_token = create_access_token(data={"sub": user_id})
            return Token(access_token=access_token)
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token has expired"
            )
        except jwt.InvalidTokenError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
