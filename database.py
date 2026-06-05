from typing import Generator

from sqlmodel import Session, SQLModel, create_engine

from core.config import settings

# connect_args required for SQLite to work with FastAPI's threading model
connect_args = {"check_same_thread": False}
engine = create_engine(settings.DATABASE_URL, connect_args=connect_args, echo=settings.DEBUG)


def create_db_and_tables() -> None:
    """Create all tables defined in SQLModel metadata."""
    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, None, None]:
    """FastAPI dependency that yields a database session."""
    with Session(engine) as session:
        yield session
