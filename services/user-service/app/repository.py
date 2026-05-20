from sqlalchemy.orm import Session
from app.models import User
from app.schemas import UserCreate, UserUpdate


def create_user(db: Session, data: UserCreate) -> User:
    user = User(
        username=data.username,
        email=data.email,
        bio=data.bio,
        avatar_url=data.avatar_url,
        gdpr_consent=data.gdpr_consent,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_user(db: Session, user_id: str) -> User | None:
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_username(db: Session, username: str) -> User | None:
    return db.query(User).filter(User.username == username).first()


def list_users(db: Session, limit: int = 20, offset: int = 0) -> tuple[list[User], int]:
    total = db.query(User).count()
    users = db.query(User).offset(offset).limit(limit).all()
    return users, total


def update_user(db: Session, user: User, data: UserUpdate) -> User:
    if data.bio is not None:
        user.bio = data.bio
    if data.avatar_url is not None:
        user.avatar_url = data.avatar_url
    if data.gdpr_consent is not None:
        user.gdpr_consent = data.gdpr_consent
    db.commit()
    db.refresh(user)
    return user


def delete_user(db: Session, user: User) -> None:
    db.delete(user)
    db.commit()
