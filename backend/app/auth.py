from datetime import datetime, timedelta

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from passlib.hash import pbkdf2_sha256
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Student
from app.config import get_settings

settings = get_settings()

bearer_scheme = HTTPBearer(auto_error=False)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pbkdf2_sha256.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    # Portable hashing (avoids bcrypt backend issues in constrained envs)
    return pbkdf2_sha256.hash(password)


def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def get_current_student(
    creds: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> Student:
    if creds is None or not creds.credentials:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    token = creds.credentials
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email = payload.get("sub")
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    if not email:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    student = db.query(Student).filter(Student.email == email).first()
    if not student:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return student


def _admin_idents() -> set[str]:
    return {s.strip() for s in (settings.ADMIN_IDENTIFIERS or "").split(",") if s.strip()}


def require_admin(student: Student = Depends(get_current_student)) -> Student:
    admin_idents = _admin_idents()
    if student.email not in admin_idents and student.student_id not in admin_idents:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin only")
    return student


def is_admin(student: Student) -> bool:
    admin_idents = _admin_idents()
    return student.email in admin_idents or student.student_id in admin_idents
