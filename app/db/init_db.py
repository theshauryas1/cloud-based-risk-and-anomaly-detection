"""
app/db/init_db.py — Creates all tables on startup (auto-migration for dev/staging).
NOTE: In production, use managed migrations (e.g. Alembic) instead of create_all().
      See README for the Alembic migration guide.
"""
from app.db.models import Base
from app.db.session import engine


def init_db() -> None:
    """Create all database tables if they don't exist yet."""
    Base.metadata.create_all(bind=engine)
