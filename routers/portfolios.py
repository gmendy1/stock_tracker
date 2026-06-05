from datetime import datetime, timezone
from typing import List

from fastapi import APIRouter, HTTPException, status
from sqlmodel import select

from models.portfolio import Portfolio, PortfolioCreate, PortfolioRead, PortfolioUpdate
from routers.deps import CurrentUser, DBSession

router = APIRouter(prefix="/portfolios", tags=["portfolios"])


@router.get("/", response_model=List[PortfolioRead])
def list_portfolios(current_user: CurrentUser, session: DBSession):
    """List all portfolios owned by the current user."""
    portfolios = session.exec(
        select(Portfolio).where(Portfolio.owner_id == current_user.id)
    ).all()
    return portfolios


@router.post("/", response_model=PortfolioRead, status_code=status.HTTP_201_CREATED)
def create_portfolio(portfolio_in: PortfolioCreate, current_user: CurrentUser, session: DBSession):
    """Create a new portfolio for the current user."""
    portfolio = Portfolio(**portfolio_in.model_dump(), owner_id=current_user.id)
    session.add(portfolio)
    session.commit()
    session.refresh(portfolio)
    return portfolio


@router.get("/{portfolio_id}", response_model=PortfolioRead)
def get_portfolio(portfolio_id: int, current_user: CurrentUser, session: DBSession):
    """Get a single portfolio by ID (must belong to current user)."""
    portfolio = _get_owned_portfolio(portfolio_id, current_user.id, session)
    return portfolio


@router.patch("/{portfolio_id}", response_model=PortfolioRead)
def update_portfolio(
    portfolio_id: int,
    updates: PortfolioUpdate,
    current_user: CurrentUser,
    session: DBSession,
):
    """Partially update a portfolio."""
    portfolio = _get_owned_portfolio(portfolio_id, current_user.id, session)
    update_data = updates.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(portfolio, field, value)
    portfolio.updated_at = datetime.now(timezone.utc)
    session.add(portfolio)
    session.commit()
    session.refresh(portfolio)
    return portfolio


@router.delete("/{portfolio_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_portfolio(portfolio_id: int, current_user: CurrentUser, session: DBSession):
    """Delete a portfolio and all its investments."""
    portfolio = _get_owned_portfolio(portfolio_id, current_user.id, session)
    session.delete(portfolio)
    session.commit()


# ── Helpers ───────────────────────────────────────────────────────────────────

def _get_owned_portfolio(portfolio_id: int, user_id: int, session) -> Portfolio:
    portfolio = session.get(Portfolio, portfolio_id)
    if not portfolio or portfolio.owner_id != user_id:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    return portfolio
