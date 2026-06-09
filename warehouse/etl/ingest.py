#!/usr/bin/env python3
"""CLI: ingest one or more AutoPTS result XML files into the warehouse.

Usage:
    python -m etl.ingest /tmp/all_stats_results.xml [/path/to/another.xml ...]
"""

import sys
import uuid
from pathlib import Path

from .db import (
    bootstrap,
    connect,
    file_already_ingested,
    insert_landing_rows,
    mark_file_ingested,
)
from .parse_results import file_hash, parse_xml


def ingest(path: Path) -> None:
    fhash = file_hash(path)
    run_id = f"{fhash[:16]}-{uuid.uuid4().hex[:8]}"

    with connect() as conn:
        bootstrap(conn)

        if file_already_ingested(conn, str(path)):
            print(f"[skip] already ingested: {path}")
            return

        rows = parse_xml(path)
        n = insert_landing_rows(conn, run_id, str(path), rows)
        mark_file_ingested(conn, str(path), fhash, run_id)

    print(f"[ok]   {n} rows loaded — run_id={run_id}  ({path})")


def main() -> None:
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    for arg in sys.argv[1:]:
        path = Path(arg)
        if not path.exists():
            print(f"[err]  file not found: {path}", file=sys.stderr)
            continue
        ingest(path)


if __name__ == "__main__":
    main()
