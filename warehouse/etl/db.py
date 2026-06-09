"""Database helpers: connection, DDL bootstrap, and raw-layer inserts."""

import os
from contextlib import contextmanager
from pathlib import Path

import psycopg2
import psycopg2.extras


def get_dsn() -> str:
    return os.environ.get(
        "AUTOPTS_WH_DSN",
        "host=localhost port=5432 dbname=autopts user=autopts password=autopts",
    )


@contextmanager
def connect():
    conn = psycopg2.connect(get_dsn())
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def bootstrap(conn) -> None:
    """Create schemas and tables from SQL files (idempotent)."""
    sql_dir = Path(__file__).parent.parent / "sql"
    with conn.cursor() as cur:
        for sql_file in sorted(sql_dir.glob("*.sql")):
            cur.execute(sql_file.read_text())


def file_already_ingested(conn, file_path: str) -> bool:
    with conn.cursor() as cur:
        cur.execute(
            "SELECT 1 FROM raw.ingested_files WHERE file_path = %s", (file_path,)
        )
        return cur.fetchone() is not None


def insert_landing_rows(conn, run_id: str, source_file: str, rows: list[dict]) -> int:
    if not rows:
        return 0
    cols = [
        "run_id", "source_file",
        "name", "project", "status", "status_previous",
        "regression", "progress", "new_case",
        "duration", "run_count", "description",
        "test_start_time", "test_end_time",
    ]
    records = [
        (
            run_id, source_file,
            r["name"], r["project"], r["status"], r["status_previous"],
            r["regression"], r["progress"], r["new_case"],
            r["duration"], r["run_count"], r["description"],
            r["test_start_time"], r["test_end_time"],
        )
        for r in rows
    ]
    with conn.cursor() as cur:
        psycopg2.extras.execute_values(
            cur,
            f"""
            INSERT INTO raw.test_results_landing ({", ".join(cols)})
            VALUES %s
            ON CONFLICT (run_id, name) DO NOTHING
            """,
            records,
        )
    return len(records)


def mark_file_ingested(conn, file_path: str, file_hash: str, run_id: str) -> None:
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO raw.ingested_files (file_path, file_hash, run_id)
            VALUES (%s, %s, %s)
            ON CONFLICT (file_path) DO NOTHING
            """,
            (file_path, file_hash, run_id),
        )
