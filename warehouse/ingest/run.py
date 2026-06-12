"""Entry point: ingest all PTS XML files for a given CI run into the warehouse."""

import argparse
import logging
import sys
from pathlib import Path

from .db import bootstrap, file_already_ingested, get_connection, insert_row
from .parse import parse_file


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s',
)
log = logging.getLogger(__name__)


def main(run_id: str, run_folder: Path) -> int:
    xml_dir = run_folder / 'XMLs'
    if not xml_dir.exists():
        log.error('XMLs directory not found: %s', xml_dir)
        return 1

    xml_files = sorted(xml_dir.glob('*.xml'))
    if not xml_files:
        log.warning('No XML files found in %s', xml_dir)
        return 0

    conn = get_connection()
    bootstrap(conn)

    partial = file_already_ingested(conn, run_id, xml_files[0])
    if partial:
        log.warning(
            'Run %s appears to be partially ingested — resuming. '
            'This may indicate a previous run crashed.',
            run_id,
        )

    succeeded = 0
    skipped = 0
    failed = 0

    for path in xml_files:
        if file_already_ingested(conn, run_id, path):
            log.info('Skipping already ingested file: %s', path.name)
            skipped += 1
            continue

        try:
            row = parse_file(path)
        except ValueError as e:
            log.error('Failed to parse %s: %s', path.name, e)
            failed += 1
            continue

        insert_row(conn, run_id, row)
        succeeded += 1

    conn.close()

    log.info(
        'Ingest complete for run %s — succeeded: %d, skipped: %d, failed: %d',
        run_id, succeeded, skipped, failed,
    )

    return 0 if failed == 0 else 1


def _parse_args():
    parser = argparse.ArgumentParser(
        description='Ingest AutoPTS PTS log XML files into the warehouse.',
    )
    parser.add_argument('run_id', help='CI job ID (used as run identifier)')
    parser.add_argument('run_folder', help='Path to the CI job folder containing XMLs/')
    return parser.parse_args()


if __name__ == '__main__':
    args = _parse_args()
    sys.exit(main(args.run_id, Path(args.run_folder)))
