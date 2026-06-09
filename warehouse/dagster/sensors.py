"""Dagster sensor: watches a directory for new AutoPTS result XML files."""

import os
from pathlib import Path

from dagster import (
    RunRequest,
    SensorEvaluationContext,
    sensor,
)

from .assets import ingest_result_file


SCAN_DIR = os.environ.get("AUTOPTS_RESULTS_SCAN_DIR", "/tmp/autopts_results")
RESULT_GLOB = "*.xml"


@sensor(asset_selection=[ingest_result_file], minimum_interval_seconds=300)
def result_file_sensor(context: SensorEvaluationContext):
    """Emit a run request for each XML file not yet seen in the scan directory."""
    scan_dir = Path(SCAN_DIR)
    if not scan_dir.exists():
        context.log.warning(f"Scan dir does not exist: {scan_dir}")
        return

    cursor_files: set[str] = set(context.cursor.split("\n")) if context.cursor else set()
    new_files = []

    for xml_file in sorted(scan_dir.glob(RESULT_GLOB)):
        fpath = str(xml_file.resolve())
        if fpath not in cursor_files:
            new_files.append(fpath)

    for fpath in new_files:
        yield RunRequest(
            run_key=fpath,
            run_config={"ops": {"ingest_result_file": {"config": {"file_path": fpath}}}},
            tags={"source_file": fpath},
        )

    if new_files:
        context.update_cursor("\n".join(cursor_files | set(new_files)))
