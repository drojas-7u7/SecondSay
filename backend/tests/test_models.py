from sqlalchemy import create_engine, inspect

from app.models import Base


def test_persistence_schema_contains_vertical_slice_tables() -> None:
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)

    inspector = inspect(engine)

    assert set(inspector.get_table_names()) == {
        "ai_decisions",
        "audits",
        "cases",
    }

    engine.dispose()


def test_ai_decision_references_case() -> None:
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)

    foreign_keys = inspect(engine).get_foreign_keys("ai_decisions")

    assert foreign_keys[0]["referred_table"] == "cases"

    engine.dispose()


def test_audit_references_ai_decision() -> None:
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)

    foreign_keys = inspect(engine).get_foreign_keys("audits")

    assert foreign_keys[0]["referred_table"] == "ai_decisions"

    engine.dispose()
