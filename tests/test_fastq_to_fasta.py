from __future__ import annotations

from pathlib import Path
from typing import NamedTuple

import pytest

from utils import fastq_to_fasta, is_fasta, is_fastq

TEST_DATA_DIR = Path(__file__).parent / Path(__file__).stem


class FastqConversionTest(NamedTuple):
    fasta_filename: str
    fastq_filename: str

    def validate(self, tmp_path: Path) -> None:
        fasta_path = TEST_DATA_DIR / self.fasta_filename
        fastq_path = TEST_DATA_DIR / self.fastq_filename
        output_path = tmp_path / self.fastq_filename

        assert is_fasta(fasta_path)
        assert is_fastq(fasta_path)

        fastq_to_fasta(fasta_path, output_path)

        assert output_path.exists()

        with open(output_path, "r") as output_file:
            with open(fastq_path, "r") as expected_file:
                output_data = output_file.read()
                fixture_data = expected_file.read()
                assert output_data == fixture_data


fastq_to_fasta_tests = [
    FastqConversionTest("simple.fastq", "simple.fasta"),
    FastqConversionTest("spaces.fastq", "simple.fasta"),
    FastqConversionTest("special.fastq", "simple.fasta"),
    FastqConversionTest("multiline.fastq", "multiline.fasta"),
]


@pytest.mark.parametrize("test", fastq_to_fasta_tests)
def test_fastq_to_fasta(test: FastqConversionTest, tmp_path: Path) -> None:
    test.validate(tmp_path)
