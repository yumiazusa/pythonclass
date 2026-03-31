from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import get_password_hash, verify_password
from app.models.user import User
from app.schemas.user import UserCreate


def get_by_username(db: Session, username: str) -> User | None:
    statement = select(User).where(User.username == username)
    return db.execute(statement).scalar_one_or_none()


def get_by_student_no(db: Session, student_no: str) -> User | None:
    statement = select(User).where(User.student_no == student_no)
    return db.execute(statement).scalar_one_or_none()


def get_by_id(db: Session, user_id: int) -> User | None:
    return db.get(User, user_id)


def create(db: Session, user_in: UserCreate) -> User:
    user = User(
        username=user_in.username,
        password_hash=get_password_hash(user_in.password),
        role=user_in.role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def create_student_by_import(
    db: Session,
    *,
    username: str,
    student_no: str,
    class_name: str,
    full_name: str,
    default_password: str,
) -> User:
    user = User(
        username=username,
        password_hash=get_password_hash(default_password),
        role="student",
        must_change_password=True,
        student_no=student_no,
        class_name=class_name,
        full_name=full_name,
    )
    db.add(user)
    db.flush()
    return user


def authenticate(db: Session, username: str, password: str) -> User | None:
    user = get_by_username(db, username=username)
    if not user:
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user
