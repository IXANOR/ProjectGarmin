import os
from pathlib import Path
import uuid

import pytest
import sys


# Ensure project root is on sys.path so `import app` works when pytest's testpaths is `tests`
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


@pytest.fixture(autouse=True)
def use_temp_db(tmp_path, monkeypatch):
    db_file = tmp_path / f"test-{uuid.uuid4().hex}.db"
    monkeypatch.setenv("APP_DB_URL", f"sqlite:///{db_file}")
    # Ensure directory exists
    Path(db_file).parent.mkdir(parents=True, exist_ok=True)

    # Create a per-test engine and override FastAPI dependency to use it
    from sqlmodel import SQLModel, create_engine, Session as SQLSession
    from app.main import app
    from app.core.db import get_session as app_get_session

    connect_args = {"check_same_thread": False}
    engine = create_engine(f"sqlite:///{db_file}", connect_args=connect_args)
    SQLModel.metadata.create_all(engine)

    def override_get_session():
        with SQLSession(engine) as session:
            yield session

    app.dependency_overrides[app_get_session] = override_get_session
    yield
    # Cleanup override
    app.dependency_overrides.pop(app_get_session, None)


