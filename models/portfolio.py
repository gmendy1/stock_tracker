from datetime import datetime, timezone
from typing import Optional, List, TYPE_CHECKING

from sqlmodel import Field, SQLModel, Relationship

if TYPE_CHECKING:
    from models.user import User
    from models.investment import Investment


# ── Database table ────────────────────────────────────────────────────────────

class Portfolio(SQLModel, table=True):
    __tablename__ = "portfolios"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=100)
    description: Optional[str] = Field(default=None, max_length=500)
    owner_id: int = Field(foreign_key="users.id")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    # Relationships
    owner: Optional["User"] = Relationship(back_populates="portfolios")
    investments: List["Investment"] = Relationship(back_populates="portfolio")


# ── Request / Response schemas ────────────────────────────────────────────────

class PortfolioBase(SQLModel):
    name: str
    description: Optional[str] = None


class PortfolioCreate(PortfolioBase):
    pass


class PortfolioRead(PortfolioBase):
    id: int
    owner_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class PortfolioUpdate(SQLModel):
    name: Optional[str] = None
    description: Optional[str] = None
