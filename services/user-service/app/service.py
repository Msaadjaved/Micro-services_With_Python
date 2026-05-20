from sqlalchemy.orm import Session
from app import repository
from app.schemas import UserCreate, UserUpdate, UserOut, UserList


def add_user(db: Session, data: UserCreate) -> UserOut:
    if repository.get_user_by_username(db, data.username):
        raise ValueError(f"Username '{data.username}' is already taken")
    user = repository.create_user(db, data)
    return UserOut.model_validate(user)


def fetch_user(db: Session, user_id: str) -> UserOut:
    user = repository.get_user(db, user_id)
    if user is None:
        raise ValueError(f"User {user_id} not found")
    return UserOut.model_validate(user)


def fetch_all_users(db: Session, limit: int = 20, offset: int = 0) -> UserList:
    users, total = repository.list_users(db, limit=limit, offset=offset)
    return UserList(
        items=[UserOut.model_validate(u) for u in users],
        total=total,
        limit=limit,
        offset=offset,
    )


def edit_user(db: Session, user_id: str, data: UserUpdate) -> UserOut:
    user = repository.get_user(db, user_id)
    if user is None:
        raise ValueError(f"User {user_id} not found")
    user = repository.update_user(db, user, data)
    return UserOut.model_validate(user)


def remove_user(db: Session, user_id: str) -> None:
    user = repository.get_user(db, user_id)
    if user is None:
        raise ValueError(f"User {user_id} not found")
    repository.delete_user(db, user)
