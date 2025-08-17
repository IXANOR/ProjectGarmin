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
                # files: add is_soft_deleted if missing
                rows = conn.exec_driver_sql("PRAGMA table_info(files)").fetchall()
                col_names = [r[1] for r in rows] if rows else []
                if "is_soft_deleted" not in col_names:
                    conn.exec_driver_sql(
                        "ALTER TABLE files ADD COLUMN is_soft_deleted BOOLEAN NOT NULL DEFAULT 0"
                    )
                # messages: add is_trimmed if missing
                rows_m = conn.exec_driver_sql("PRAGMA table_info(messages)").fetchall()
                col_m = [r[1] for r in rows_m] if rows_m else []
                if "is_trimmed" not in col_m:
                    conn.exec_driver_sql(
                        "ALTER TABLE messages ADD COLUMN is_trimmed BOOLEAN NOT NULL DEFAULT 0"
                    )
                # themesettingsmodel: add panel_color / border_color if missing
                rows_t = conn.exec_driver_sql("PRAGMA table_info(themesettingsmodel)").fetchall()
                col_t = [r[1] for r in rows_t] if rows_t else []
                if "panel_color" not in col_t:
                    conn.exec_driver_sql(
                        "ALTER TABLE themesettingsmodel ADD COLUMN panel_color TEXT DEFAULT '#ffffff'"
                    )
                if "border_color" not in col_t:
                    conn.exec_driver_sql(
                        "ALTER TABLE themesettingsmodel ADD COLUMN border_color TEXT DEFAULT '#e5e7eb'"
                    )
                # themepresetmodel: add panel_color / border_color if missing
                rows_tp = conn.exec_driver_sql("PRAGMA table_info(themepresetmodel)").fetchall()
                col_tp = [r[1] for r in rows_tp] if rows_tp else []
                if "panel_color" not in col_tp:
                    conn.exec_driver_sql(
                        "ALTER TABLE themepresetmodel ADD COLUMN panel_color TEXT DEFAULT '#ffffff'"
                    )
                if "border_color" not in col_tp:
                    conn.exec_driver_sql(
                        "ALTER TABLE themepresetmodel ADD COLUMN border_color TEXT DEFAULT '#e5e7eb'"
                    )
                # globals default max_tokens/frequency_penalty migration if row exists with old defaults
                rows_g = conn.exec_driver_sql("PRAGMA table_info(globalsettingsmodel)").fetchall()
                # Attempt a safe default upgrade for existing row with legacy defaults
                try:
                    cur = conn.exec_driver_sql("SELECT id, max_tokens, frequency_penalty FROM globalsettingsmodel WHERE id=1").fetchone()
                    if cur is not None:
                        cur_max = cur[1]
                        cur_freq = cur[2]
                        # If old defaults detected, upgrade them
                        if cur_max == 1024:
                            conn.exec_driver_sql("UPDATE globalsettingsmodel SET max_tokens=12000 WHERE id=1")
                        if cur_freq == 0.0:
                            conn.exec_driver_sql("UPDATE globalsettingsmodel SET frequency_penalty=1.1 WHERE id=1")
                except Exception:
                    pass
        except Exception:
            # Best-effort; continue to create tables
            pass
    SQLModel.metadata.create_all(engine)


def get_session() -> Iterator[Session]:
    with Session(engine) as session:
        yield session


