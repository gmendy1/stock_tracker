from datetime import datetime, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import select

from core.security import create_access_token, hash_password, verify_password
from models.user import User, UserCreate, UserRead
from routers.deps import CurrentUser, DBSession

router = APIRouter(prefix="/auth", tags=["auth"])


# ── Schemas ───────────────────────────────────────────────────────────────────

class Token:
    access_token: str
    token_type: str


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register(user_in: UserCreate, session: DBSession):
    """Create a new user account."""
    # Check uniqueness
    existing_email = session.exec(select(User).where(User.email == user_in.email)).first()
    if existing_email:
        raise HTTPException(status_code=400, detail="Email already registered")

    existing_username = session.exec(select(User).where(User.username == user_in.username)).first()
    if existing_username:
        raise HTTPException(status_code=400, detail="Username already taken")

    user = User(
        email=user_in.email,
        username=user_in.username,
        hashed_password=hash_password(user_in.password),
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@router.post("/login")
def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: DBSession,
):
    """Authenticate with username + password and return a JWT access token."""
    user = session.exec(select(User).where(User.username == form_data.username)).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")

    token = create_access_token(subject=str(user.id))
    return {"access_token": token, "token_type": "bearer"}


@router.get("/me", response_model=UserRead)
def get_me(current_user: CurrentUser):
    """Return the currently authenticated user's profile."""
    return current_user


@router.put("/me", response_model=UserRead)
def update_me(
    updates: dict,
    current_user: CurrentUser,
    session: DBSession,
):
    """Update the currently authenticated user's profile."""
    if "password" in updates:
        current_user.hashed_password = hash_password(updates.pop("password"))
    for field, value in updates.items():
        if hasattr(current_user, field):
            setattr(current_user, field, value)
    current_user.updated_at = datetime.now(timezone.utc)
    session.add(current_user)
    session.commit()
    session.refresh(current_user)
    return current_user
