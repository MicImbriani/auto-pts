from datetime import datetime
from pathlib import Path

import pytest

from warehouse.ingest.parse import parse_file


def make_pts_xml(
    directory,
    profile='AICS',
    tc_name='SR/CP/BV-01-C',
    verdict='PASS',
    pts_version='v8.13.0 Build 4',
    timestamp='2026_06_12_01_19_53',
    log_extra='',
):
    """Write a minimal valid PTS XML file and return its Path."""
    full_tc_name = f'{profile}/{tc_name}'
    filename = f'prefix_{profile}_{tc_name.replace("/", "_")}_{timestamp}.xml'
    content = (
        '<?xml version="1.0" encoding="utf-8"?>\n'
        '<ARCHIVE>\n'
        f'  <PicsPixit>ICS VALUES:\nTSPC_{profile}_0_1 TRUE\n</PicsPixit>\n'
        f'  <LOG>\n+62 ms\nMessage: PTS: {pts_version}\n+1000 ms\nSome event\n{log_extra}\n+64953 ms\nFinal Verdict: {verdict}\n</LOG>\n'
        f'  <SUMMARY>Test case : {full_tc_name} started\nFinal Verdict:{verdict}\n{full_tc_name} finished\n</SUMMARY>\n'
        '</ARCHIVE>\n'
    )
    path = Path(directory) / filename
    path.write_text(content, encoding='utf-8')
    return path


class TestParseFile:

    def test_happy_path(self, tmp_path):
        path = make_pts_xml(tmp_path)
        result = parse_file(path)

        assert result['test_case_name'] == 'AICS/SR/CP/BV-01-C'
        assert result['final_verdict'] == 'PASS'
        assert result['started_at'] == datetime(2026, 6, 12, 1, 19, 53)
        assert result['pts_version'] == 'v8.13.0 Build 4'
        assert result['profile'] == 'AICS'
        assert result['duration_ms'] == 64953
        assert isinstance(result['pics_pixit_raw'], str)
        assert len(result['pics_pixit_raw']) > 0
        assert result['file_path'] == str(path.resolve())

    def test_started_at_parsed_from_filename(self, tmp_path):
        path = make_pts_xml(tmp_path, timestamp='2025_01_31_23_59_00')
        result = parse_file(path)
        assert result['started_at'] == datetime(2025, 1, 31, 23, 59, 0)

    def test_profile_derived_from_test_case_name(self, tmp_path):
        path = make_pts_xml(tmp_path, profile='GAP', tc_name='DM/NCON/BV-01-C')
        result = parse_file(path)
        assert result['profile'] == 'GAP'
        assert result['test_case_name'] == 'GAP/DM/NCON/BV-01-C'

    def test_duration_ms_is_largest_timestamp(self, tmp_path):
        # Ensure the parser takes the maximum +Xms value, not the first
        path = make_pts_xml(tmp_path, log_extra='+99999 ms\nSome event\n+100 ms')
        result = parse_file(path)
        assert result['duration_ms'] == 99999

    def test_non_pass_verdict(self, tmp_path):
        path = make_pts_xml(tmp_path, verdict='FAIL')
        result = parse_file(path)
        assert result['final_verdict'] == 'FAIL'

    def test_missing_summary_raises(self, tmp_path):
        path = tmp_path / 'prefix_AICS_TC_2026_06_12_01_19_53.xml'
        path.write_text(
            '<?xml version="1.0" encoding="utf-8"?>\n'
            '<ARCHIVE>\n'
            '  <PicsPixit>ICS VALUES:</PicsPixit>\n'
            '  <LOG>+62 ms</LOG>\n'
            '</ARCHIVE>\n',
            encoding='utf-8',
        )
        with pytest.raises(ValueError, match='SUMMARY'):
            parse_file(path)

    def test_missing_log_raises(self, tmp_path):
        path = tmp_path / 'prefix_AICS_TC_2026_06_12_01_19_53.xml'
        path.write_text(
            '<?xml version="1.0" encoding="utf-8"?>\n'
            '<ARCHIVE>\n'
            '  <PicsPixit>ICS VALUES:</PicsPixit>\n'
            '  <SUMMARY>Test case : AICS/TC started\nFinal Verdict:PASS\n</SUMMARY>\n'
            '</ARCHIVE>\n',
            encoding='utf-8',
        )
        with pytest.raises(ValueError, match='LOG'):
            parse_file(path)

    def test_bad_filename_timestamp_raises(self, tmp_path):
        path = tmp_path / 'no_timestamp_here.xml'
        path.write_text(
            '<?xml version="1.0" encoding="utf-8"?>\n'
            '<ARCHIVE>\n'
            '  <PicsPixit>ICS VALUES:</PicsPixit>\n'
            '  <LOG>+62 ms\nMessage: PTS: v8.13.0 Build 4\n+100 ms\n</LOG>\n'
            '  <SUMMARY>Test case : AICS/TC started\nFinal Verdict:PASS\n</SUMMARY>\n'
            '</ARCHIVE>\n',
            encoding='utf-8',
        )
        with pytest.raises(ValueError, match='timestamp'):
            parse_file(path)
