from __future__ import annotations

from pathlib import Path

from merge import get_file_groups

TEST_DATA_DIR = Path(__file__).parent / Path(__file__).stem


def test_groups_simple():
    groups = get_file_groups(TEST_DATA_DIR / "simple", r"^(\d+)")
    assert groups == {
        "123": {"123_foo.fas", "123_bar.fas"},
        "456": {"456_buz.fas"},
    }

def test_groups_real():
    groups = get_file_groups(TEST_DATA_DIR / "real", r"^(\d+)")
    assert groups == {
        "4724": {"4724_no1.fasta", "4724_no2.fasta", "4724_no3.fasta"},
        "6139": {"6139_no1.fasta", "6139_no2.fasta", "6139_no3.fasta"},
    }
