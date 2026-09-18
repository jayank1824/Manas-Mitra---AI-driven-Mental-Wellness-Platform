from datetime import datetime, timedelta, timezone
from typing import Optional
import uuid
import bcrypt
from jose import JWTError, jwt
from fastapi import Request, Response
from sqlalchemy.orm import Session
from app.config import settings
from app.models.user import User, UserProfile


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def decode_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None

def generate_verification_token() -> str:
    return str(uuid.uuid4())

def get_current_user_from_cookie(request: Request, db: Session) -> Optional[User]:
    token = request.cookies.get("access_token")
    if not token:
        return None
    payload = decode_token(token)
    if not payload:
        return None
    user_id = payload.get("sub")
    if not user_id:
        return None
    user = db.query(User).filter(User.id == int(user_id)).first()
    return user

def create_user(db: Session, email: str, name: str, password: str, phone: str = None) -> User:
    verification_token = generate_verification_token()
    user = User(
        email=email,
        name=name,
        password_hash=hash_password(password),
        phone=phone,
        is_verified=True,  # Auto-verify for dev
        verification_token=verification_token
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Create empty profile
    profile = UserProfile(user_id=user.id)
    db.add(profile)
    db.commit()
    
    # Print verification link to console
    print(f"\n{'='*60}")
    print(f"VERIFICATION LINK for {email}:")
    print(f"http://localhost:8000/auth/verify/{verification_token}")
    print(f"{'='*60}\n")
    
    return user

def set_auth_cookie(response: Response, user: User) -> Response:
    token = create_access_token({"sub": str(user.id), "email": user.email})
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        samesite="lax"
    )
    return response
