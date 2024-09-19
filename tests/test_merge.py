from __future__ import annotations

from pathlib import Path

from merge import get_file_groups, merge_fasta_files

from .pytest_utils import assert_file_equals

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


def test_merge_simple_keep(tmp_path: Path):
    parent = TEST_DATA_DIR / "simple"
    target_path = tmp_path / "123_merged.fas"
    expected_path = parent / "keep" / "123_merged.fas"
    input_paths = [
        parent / "123_foo.fas",
        parent / "123_bar.fas",
    ]
    merge_fasta_files(input_paths, target_path, False)
    assert_file_equals(target_path, expected_path)

    target_path = tmp_path / "456_merged.fas"
    expected_path = parent / "keep" / "456_merged.fas"
    input_paths = [
        parent / "456_buz.fas",
    ]
    merge_fasta_files(input_paths, target_path, False)
    assert_file_equals(target_path, expected_path)


def test_merge_simple_discard(tmp_path: Path):
    parent = TEST_DATA_DIR / "simple"
    target_path = tmp_path / "123_merged.fas"
    expected_path = parent / "discard" / "123_merged.fas"
    input_paths = [
        parent / "123_foo.fas",
        parent / "123_bar.fas",
    ]
    merge_fasta_files(input_paths, target_path, True)
    assert_file_equals(target_path, expected_path)

    target_path = tmp_path / "456_merged.fas"
    expected_path = parent / "discard" / "456_merged.fas"
    input_paths = [
        parent / "456_buz.fas",
    ]
    merge_fasta_files(input_paths, target_path, True)
    assert_file_equals(target_path, expected_path)


def test_merge_real_keep(tmp_path: Path):
    parent = TEST_DATA_DIR / "real"
    target_path = tmp_path / "4724_merged.fasta"
    expected_path = parent / "keep" / "4724_merged.fasta"
    input_paths = [
        parent / "4724_no1.fasta",
        parent / "4724_no2.fasta",
        parent / "4724_no3.fasta",
    ]
    merge_fasta_files(input_paths, target_path, False)
    assert_file_equals(target_path, expected_path)

    target_path = tmp_path / "6139_merged.fasta"
    expected_path = parent / "keep" / "6139_merged.fasta"
    input_paths = [
        parent / "6139_no1.fasta",
        parent / "6139_no2.fasta",
        parent / "6139_no3.fasta",
    ]
    merge_fasta_files(input_paths, target_path, False)
    assert_file_equals(target_path, expected_path)


def test_merge_real_discard(tmp_path: Path):
    parent = TEST_DATA_DIR / "real"
    target_path = tmp_path / "4724_merged.fasta"
    expected_path = parent / "discard" / "4724_merged.fasta"
    input_paths = [
        parent / "4724_no1.fasta",
        parent / "4724_no2.fasta",
        parent / "4724_no3.fasta",
    ]
    merge_fasta_files(input_paths, target_path, True)
    assert_file_equals(target_path, expected_path)

    target_path = tmp_path / "6139_merged.fasta"
    expected_path = parent / "discard" / "6139_merged.fasta"
    input_paths = [
        parent / "6139_no1.fasta",
        parent / "6139_no2.fasta",
        parent / "6139_no3.fasta",
    ]
    merge_fasta_files(input_paths, target_path, True)
    assert_file_equals(target_path, expected_path)
