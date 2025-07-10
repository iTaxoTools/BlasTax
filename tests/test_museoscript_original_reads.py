from __future__ import annotations

from pathlib import Path
from typing import NamedTuple

import pytest

from itaxotools.blastax.core import museoscript_original_reads

TEST_DATA_DIR = Path(__file__).parent / Path(__file__).stem


class MuseoOrigTest(NamedTuple):
    blast_path: str
    orig_query: str
    output_path: str
    pident_threshold: float
    expected_output: str

    def validate(self, tmp_path: Path) -> None:
        blast_path = TEST_DATA_DIR / self.blast_path
        orig_query = TEST_DATA_DIR / self.orig_query
        output_path = tmp_path / self.output_path
        expected_output = TEST_DATA_DIR / self.expected_output
        museoscript_original_reads(
            str(blast_path),
            str(orig_query),
            str(output_path),
            self.pident_threshold,
        )

        assert output_path.exists()

        # Verify that the output matches the expected output
        with open(output_path, "r") as output_file:
            output_data = output_file.read()

        with open(expected_output, "r") as expected_file:
            expected_data = expected_file.read()

        assert output_data == expected_data
        print("Output matches expected output.")


# New blast tests
museo_orig_tests = [
    MuseoOrigTest(
        "blast_output_fastq_expected.out",
        "HI.4019.002.index_7.ANN0831_R1_small.fasta",
        "museoscript_output_orig.out",
        0.9,
        "museoscript_output_orig_expected.out",
    ),
MuseoOrigTest(
        "blast_output_fastq_expected.out",
        "HI.4019.002.index_7.ANN0831_R1_small_multilines.fasta",
        "museoscript_output_orig_multilines.out",
        0.9,
        "museoscript_output_orig_expected.out",
    ),
]


@pytest.mark.parametrize("test", museo_orig_tests)
def test_museoscript(test: MuseoOrigTest, tmp_path: Path) -> None:
    test.validate(tmp_path)
