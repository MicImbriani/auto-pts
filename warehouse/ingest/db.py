"""Database adapter layer. Only this file knows we are using DuckDB."""

import os
from datetime import datetime, timezone

import duckdb


_DEFAULT_DB_PATH = './autopts_warehouse.duckdb'

_CREATE_BRONZE = """
CREATE TABLE IF NOT EXISTS bronze_test_results (
    file_path       TEXT,
    run_id          TEXT,
    ingested_at     TIMESTAMP,
    test_case_name  TEXT,
    final_verdict   TEXT,
    started_at      TIMESTAMP,
    pts_version     TEXT,
    profile         TEXT,
    duration_ms     INTEGER,
    pics_pixit_raw  TEXT
)
"""


def get_connection():
    path = os.environ.get('AUTOPTS_WH_PATH', _DEFAULT_DB_PATH)
    return duckdb.connect(path)


def bootstrap(conn):
    conn.execute(_CREATE_BRONZE)


def file_already_ingested(conn, run_id: str, path) -> bool:
    result = conn.execute(
        'SELECT COUNT(*) FROM bronze_test_results WHERE run_id = ? AND file_path = ?',
        [run_id, str(path)],
    ).fetchone()
    return result[0] > 0


def insert_row(conn, run_id: str, row: dict) -> None:
    conn.execute(
        """
        INSERT INTO bronze_test_results (
            file_path, run_id, ingested_at,
            test_case_name, final_verdict, started_at,
            pts_version, profile, duration_ms, pics_pixit_raw
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        [
            row['file_path'],
            run_id,
            datetime.now(timezone.utc),
            row['test_case_name'],
            row['final_verdict'],
            row['started_at'],
            row['pts_version'],
            row['profile'],
            row['duration_ms'],
            row['pics_pixit_raw'],
        ],
    )
