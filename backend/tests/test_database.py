import pytest
from sqlalchemy import text

from app.core.database import build_engine, build_session_factory


def test_build_engine_connects_with_sqlalchemy() -> None:
    engine = build_engine("sqlite+pysqlite:///:memory:")

    with engine.connect() as connection:
        assert connection.scalar(text("SELECT 1")) == 1

    engine.dispose()


def test_session_factory_creates_working_session() -> None:
    engine = build_engine("sqlite+pysqlite:///:memory:")
    session_factory = build_session_factory(engine)

    with session_factory() as session:
        assert session.scalar(text("SELECT 1")) == 1

    engine.dispose()


def test_build_engine_rejects_blank_database_url() -> None:
    with pytest.raises(ValueError, match="DATABASE_URL is not configured"):
        build_engine("")
