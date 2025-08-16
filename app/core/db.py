import os
from pathlib import Path
from typing import Iterator

from sqlmodel import SQLModel, Session, create_engine


def _get_database_url() -> str:
    env_url = os.getenv("APP_DB_URL")
    if env_url:
        return env_url
    # Default to local data directory
    data_dir = Path("data")
    data_dir.mkdir(parents=True, exist_ok=True)
    return f"sqlite:///{data_dir / 'app.db'}"


DATABASE_URL = _get_database_url()


connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args)


def init_db() -> None:
    # Ensure default data dir exists for sqlite file URLs
    if DATABASE_URL.startswith("sqlite") and ":memory:" not in DATABASE_URL:
        db_path = DATABASE_URL.replace("sqlite:///", "")
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        # Lightweight migration: add missing columns when upgrading schema
        try:
            from sqlalchemy import text
            with engine.begin() as conn:
                rows = conn.exec_driver_sql("PRAGMA table_info(files)").fetchall()
                col_names = [r[1] for r in rows] if rows else []
                if "is_soft_deleted" not in col_names:
                    conn.exec_driver_sql(
                        "ALTER TABLE files ADD COLUMN is_soft_deleted BOOLEAN NOT NULL DEFAULT 0"
                    )
        except Exception:
            # Best-effort; continue to create tables
            pass
    SQLModel.metadata.create_all(engine)


def get_session() -> Iterator[Session]:
    with Session(engine) as session:
        yield session


