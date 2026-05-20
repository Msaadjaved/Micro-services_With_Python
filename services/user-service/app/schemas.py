from pydantic import BaseModel, EmailStr
from datetime import datetime


class UserCreate(BaseModel):
    username: str
    email: str
    bio: str | None = None
    avatar_url: str | None = None
    gdpr_consent: bool = False


class UserUpdate(BaseModel):
    bio: str | None = None
    avatar_url: str | None = None
    gdpr_consent: bool | None = None


class UserOut(BaseModel):
    id: str
    username: str
    email: str
    bio: str | None
    avatar_url: str | None
    gdpr_consent: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class UserList(BaseModel):
    items: list[UserOut]
    total: int
    limit: int
    offset: int
