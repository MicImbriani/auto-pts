"""Parse AutoPTS result XML into rows ready for raw.test_results_landing."""

import hashlib
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


_DT_FMT = "%Y-%m-%d %H:%M:%S"


def _parse_dt(value: Optional[str]) -> Optional[datetime]:
    if not value:
        return None
    try:
        return datetime.strptime(value, _DT_FMT).replace(tzinfo=timezone.utc)
    except ValueError:
        return None


def _parse_bool(value: Optional[str]) -> Optional[bool]:
    if value is None:
        return None
    return value.strip().lower() in ("true", "1", "yes")


def file_hash(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def parse_xml(path: Path) -> list[dict]:
    """Return a list of row dicts, one per <test_case> element."""
    tree = ET.parse(path)
    root = tree.getroot()

    rows = []
    for tc in root.iter("test_case"):
        name = tc.get("name", "")
        project = tc.get("project") or (name.split("/")[0] if "/" in name else None)
        case_name = name.split("/", 1)[1] if "/" in name else name

        rows.append({
            "name":            name,
            "project":         project,
            "case_name":       case_name,
            "status":          tc.get("status"),
            "status_previous": tc.get("status_previous"),
            "regression":      _parse_bool(tc.get("regression")),
            "progress":        _parse_bool(tc.get("progress")),
            "new_case":        tc.get("new") == "1",
            "duration":        float(tc.get("duration")) if tc.get("duration") else None,
            "run_count":       int(tc.get("run_count")) if tc.get("run_count") else None,
            "description":     tc.get("description"),
            "test_start_time": _parse_dt(tc.get("test_start_time")),
            "test_end_time":   _parse_dt(tc.get("test_end_time")),
        })

    return rows
