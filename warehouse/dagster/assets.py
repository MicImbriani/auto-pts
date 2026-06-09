"""Dagster assets for loading AutoPTS result XML into raw landing table."""

import hashlib
import uuid
from datetime import datetime, timezone
from pathlib import Path

from dagster import (
    AssetExecutionContext,
    Config,
    asset,
)

from etl.db import (
    bootstrap,
    connect,
    file_already_ingested,
    insert_landing_rows,
    mark_file_ingested,
)
from etl.parse_results import file_hash, parse_xml


class IngestConfig(Config):
    file_path: str


@asset(group_name="ingest")
def ingest_result_file(context: AssetExecutionContext, config: IngestConfig) -> dict:
    """Parse one AutoPTS result XML file and load it into raw.test_results_landing."""
    path = Path(config.file_path)
    if not path.exists():
        raise FileNotFoundError(f"Result file not found: {path}")

    fhash = file_hash(path)
    run_id = f"{fhash[:16]}-{uuid.uuid4().hex[:8]}"

    with connect() as conn:
        bootstrap(conn)

        if file_already_ingested(conn, str(path)):
            context.log.info(f"Already ingested: {path} — skipping")
            return {"skipped": True, "file": str(path)}

        rows = parse_xml(path)
        n = insert_landing_rows(conn, run_id, str(path), rows)
        mark_file_ingested(conn, str(path), fhash, run_id)

    context.log.info(f"Loaded {n} rows from {path} (run_id={run_id})")
    return {"run_id": run_id, "rows_loaded": n, "file": str(path)}
