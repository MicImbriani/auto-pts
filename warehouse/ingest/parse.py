"""Parse a single PTS log XML file into a dict of extracted fields."""

import re
from datetime import datetime
from pathlib import Path
from xml.etree import ElementTree


_FILENAME_TS_RE = re.compile(r'_(\d{4}_\d{2}_\d{2}_\d{2}_\d{2}_\d{2})\.xml$')
_FILENAME_TS_FMT = '%Y_%m_%d_%H_%M_%S'
_PTS_VERSION_RE = re.compile(r'PTS:\s*(v[\d.]+ Build \d+)')
_DURATION_RE = re.compile(r'\+(\d+) ms')
_SUMMARY_NAME_RE = re.compile(r'Test case\s*:\s*(.+?)\s+started', re.IGNORECASE)
_SUMMARY_VERDICT_RE = re.compile(r'Final Verdict\s*:\s*(\S+)', re.IGNORECASE)


def parse_file(path: Path) -> dict:
    path = Path(path)

    tree = ElementTree.parse(path)
    root = tree.getroot()

    pics_pixit_el = root.find('PicsPixit')
    log_el = root.find('LOG')
    summary_el = root.find('SUMMARY')

    if summary_el is None:
        raise ValueError(f'Missing <SUMMARY> element in {path}')
    if log_el is None:
        raise ValueError(f'Missing <LOG> element in {path}')
    if pics_pixit_el is None:
        raise ValueError(f'Missing <PicsPixit> element in {path}')

    summary_text = summary_el.text or ''
    log_text = log_el.text or ''
    pics_pixit_text = pics_pixit_el.text or ''

    # test_case_name
    name_match = _SUMMARY_NAME_RE.search(summary_text)
    if not name_match:
        raise ValueError(f'Could not extract test case name from <SUMMARY> in {path}')
    test_case_name = name_match.group(1).strip()

    # final_verdict
    verdict_match = _SUMMARY_VERDICT_RE.search(summary_text)
    if not verdict_match:
        raise ValueError(f'Could not extract final verdict from <SUMMARY> in {path}')
    final_verdict = verdict_match.group(1).strip()

    # started_at — from filename
    ts_match = _FILENAME_TS_RE.search(path.name)
    if not ts_match:
        raise ValueError(f'Could not extract timestamp from filename: {path.name}')
    started_at = datetime.strptime(ts_match.group(1), _FILENAME_TS_FMT)

    # pts_version
    pts_match = _PTS_VERSION_RE.search(log_text)
    if not pts_match:
        raise ValueError(f'Could not extract PTS version from <LOG> in {path}')
    pts_version = pts_match.group(1).strip()

    # duration_ms — last +Xms timestamp in the log
    durations = _DURATION_RE.findall(log_text)
    if not durations:
        raise ValueError(f'Could not extract duration from <LOG> in {path}')
    duration_ms = max(int(d) for d in durations)

    # profile — first segment of test case name
    profile = test_case_name.split('/')[0]

    return {
        'file_path':      str(path.resolve()),
        'test_case_name': test_case_name,
        'final_verdict':  final_verdict,
        'started_at':     started_at,
        'pts_version':    pts_version,
        'profile':        profile,
        'duration_ms':    duration_ms,
        'pics_pixit_raw': pics_pixit_text,
    }
