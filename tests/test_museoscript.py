from __future__ import annotations

from pathlib import Path
from typing import NamedTuple

import pytest

from itaxotools.blastax.core import museoscript

from .pytest_utils import assert_file_equals

TEST_DATA_DIR = Path(__file__).parent / Path(__file__).stem


class MuseoTest(NamedTuple):
    blast_filename: str
    output_filename: str
    original_reads: str | None
    deduplicate: bool
    pident_threshold: float

    def validate(self, tmp_path: Path) -> None:
        blast_path = TEST_DATA_DIR / self.blast_filename
        expected_output = TEST_DATA_DIR / self.output_filename
        original_reads_path = TEST_DATA_DIR / self.original_reads if self.original_reads else None
        output_path = tmp_path / self.output_filename
        museoscript(
            blast_path=blast_path,
            output_path=output_path,
            original_reads_path=original_reads_path,
            pident_threshold=self.pident_threshold,
            deduplicate=self.deduplicate,
        )

        assert output_path.exists()

        assert_file_equals(output_path, expected_output)


# New blast tests
museo_tests = [
    MuseoTest("parse_blast.out", "parse_museo.fas", None, False, 0.9),
    MuseoTest("parse_blast.out", "parse_museo_dedup.fas", None, True, 0.9),
    MuseoTest("original_blast.out", "original_museo.fas", "original_sequences.fas", False, 0.9),
    MuseoTest("original_blast.out", "original_museo_dedup.fas", "original_sequences.fas", True, 0.9),
]


@pytest.mark.parametrize("test", museo_tests)
def test_museoscript(test: MuseoTest, tmp_path: Path) -> None:
    test.validate(tmp_path)
