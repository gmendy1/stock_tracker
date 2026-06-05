from datetime import datetime, timezone
from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query, status
from sqlmodel import select

from models.investment import (
    Investment,
    InvestmentCreate,
    InvestmentRead,
    InvestmentUpdate,
    TransactionType,
)
from models.portfolio import Portfolio
from routers.deps import CurrentUser, DBSession

router = APIRouter(prefix="/portfolios/{portfolio_id}/investments", tags=["investments"])


@router.get("/", response_model=List[InvestmentRead])
def list_investments(
    portfolio_id: int,
    current_user: CurrentUser,
    session: DBSession,
    ticker: Optional[str] = Query(default=None, description="Filter by ticker symbol"),
    transaction_type: Optional[TransactionType] = Query(default=None),
):
    """List all investments in a portfolio, with optional filters."""
    _assert_portfolio_ownership(portfolio_id, current_user.id, session)

    query = select(Investment).where(Investment.portfolio_id == portfolio_id)
    if ticker:
        query = query.where(Investment.ticker == ticker.upper())
    if transaction_type:
        query = query.where(Investment.transaction_type == transaction_type)

    return session.exec(query).all()


@router.post("/", response_model=InvestmentRead, status_code=status.HTTP_201_CREATED)
def create_investment(
    portfolio_id: int,
    investment_in: InvestmentCreate,
    current_user: CurrentUser,
    session: DBSession,
):
    """Record a new buy or sell transaction."""
    _assert_portfolio_ownership(portfolio_id, current_user.id, session)

    data = investment_in.model_dump()
    data["ticker"] = data["ticker"].upper()
    investment = Investment(**data, portfolio_id=portfolio_id)
    session.add(investment)
    session.commit()
    session.refresh(investment)
    return investment


@router.get("/{investment_id}", response_model=InvestmentRead)
def get_investment(
    portfolio_id: int,
    investment_id: int,
    current_user: CurrentUser,
    session: DBSession,
):
    """Get a single investment record."""
    _assert_portfolio_ownership(portfolio_id, current_user.id, session)
    return _get_investment(investment_id, portfolio_id, session)


@router.patch("/{investment_id}", response_model=InvestmentRead)
def update_investment(
    portfolio_id: int,
    investment_id: int,
    updates: InvestmentUpdate,
    current_user: CurrentUser,
    session: DBSession,
):
    """Partially update an investment record."""
    _assert_portfolio_ownership(portfolio_id, current_user.id, session)
    investment = _get_investment(investment_id, portfolio_id, session)

    update_data = updates.model_dump(exclude_unset=True)
    if "ticker" in update_data:
        update_data["ticker"] = update_data["ticker"].upper()
    for field, value in update_data.items():
        setattr(investment, field, value)
    investment.updated_at = datetime.now(timezone.utc)
    session.add(investment)
    session.commit()
    session.refresh(investment)
    return investment


@router.delete("/{investment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_investment(
    portfolio_id: int,
    investment_id: int,
    current_user: CurrentUser,
    session: DBSession,
):
    """Delete an investment record."""
    _assert_portfolio_ownership(portfolio_id, current_user.id, session)
    investment = _get_investment(investment_id, portfolio_id, session)
    session.delete(investment)
    session.commit()


# ── Summary endpoint ──────────────────────────────────────────────────────────

@router.get("/summary/by-ticker")
def investment_summary(
    portfolio_id: int,
    current_user: CurrentUser,
    session: DBSession,
):
    """Return a per-ticker summary of net shares held and total cost basis."""
    _assert_portfolio_ownership(portfolio_id, current_user.id, session)
    investments = session.exec(
        select(Investment).where(Investment.portfolio_id == portfolio_id)
    ).all()

    summary: dict = {}
    for inv in investments:
        entry = summary.setdefault(inv.ticker, {"ticker": inv.ticker, "net_shares": 0.0, "cost_basis": 0.0})
        sign = 1 if inv.transaction_type == TransactionType.BUY else -1
        entry["net_shares"] += sign * inv.shares
        entry["cost_basis"] += sign * inv.total_value

    return list(summary.values())


# ── Helpers ───────────────────────────────────────────────────────────────────

def _assert_portfolio_ownership(portfolio_id: int, user_id: int, session) -> None:
    portfolio = session.get(Portfolio, portfolio_id)
    if not portfolio or portfolio.owner_id != user_id:
        raise HTTPException(status_code=404, detail="Portfolio not found")


def _get_investment(investment_id: int, portfolio_id: int, session) -> Investment:
    investment = session.get(Investment, investment_id)
    if not investment or investment.portfolio_id != portfolio_id:
        raise HTTPException(status_code=404, detail="Investment not found")
    return investment
