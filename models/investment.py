from datetime import date, datetime, timezone
from enum import Enum
from typing import Optional, TYPE_CHECKING

from sqlmodel import Field, SQLModel, Relationship

if TYPE_CHECKING:
    from models.portfolio import Portfolio


class TransactionType(str, Enum):
    BUY = "buy"
    SELL = "sell"


# ── Database table ────────────────────────────────────────────────────────────

class Investment(SQLModel, table=True):
    __tablename__ = "investments"

    id: Optional[int] = Field(default=None, primary_key=True)
    portfolio_id: int = Field(foreign_key="portfolios.id")

    # Stock details
    ticker: str = Field(max_length=10, index=True)       # e.g. AAPL, TSLA
    company_name: Optional[str] = Field(default=None, max_length=200)
    transaction_type: TransactionType = Field(default=TransactionType.BUY)

    # Trade details
    shares: float                                         # number of shares
    price_per_share: float                                # price at trade time
    transaction_date: date = Field(default_factory=date.today)
    notes: Optional[str] = Field(default=None, max_length=1000)

    # Metadata
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    # Relationships
    portfolio: Optional["Portfolio"] = Relationship(back_populates="investments")

    @property
    def total_value(self) -> float:
        return self.shares * self.price_per_share


# ── Request / Response schemas ────────────────────────────────────────────────

class InvestmentBase(SQLModel):
    ticker: str
    company_name: Optional[str] = None
    transaction_type: TransactionType = TransactionType.BUY
    shares: float
    price_per_share: float
    transaction_date: Optional[date] = None
    notes: Optional[str] = None


class InvestmentCreate(InvestmentBase):
    pass


class InvestmentRead(InvestmentBase):
    id: int
    portfolio_id: int
    total_value: float
    created_at: datetime

    class Config:
        from_attributes = True


class InvestmentUpdate(SQLModel):
    ticker: Optional[str] = None
    company_name: Optional[str] = None
    shares: Optional[float] = None
    price_per_share: Optional[float] = None
    transaction_date: Optional[date] = None
    notes: Optional[str] = None
