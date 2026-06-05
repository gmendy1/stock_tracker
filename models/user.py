from datetime import datetime, timezone
from typing import Optional, List, TYPE_CHECKING

from sqlmodel import Field, SQLModel, Relationship

if TYPE_CHECKING:
    from models.portfolio import Portfolio


# ── Database table ────────────────────────────────────────────────────────────

class User(SQLModel, table=True):
    __tablename__ = "users"

    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True, max_length=255)
    username: str = Field(unique=True, index=True, max_length=50)
    hashed_password: str
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    # Relationships
    portfolios: List["Portfolio"] = Relationship(back_populates="owner")


# ── Request / Response schemas ────────────────────────────────────────────────

class UserBase(SQLModel):
    email: str
    username: str


class UserCreate(UserBase):
    password: str


class UserRead(UserBase):
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class UserUpdate(SQLModel):
    email: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
