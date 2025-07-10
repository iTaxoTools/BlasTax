from __future__ import annotations

from pathlib import Path
from typing import NamedTuple

import pytest

from itaxotools.blastax.utils import fastq_to_fasta, is_fasta, is_fastq

TEST_DATA_DIR = Path(__file__).parent / Path(__file__).stem


class FastqConversionTest(NamedTuple):
    fastq_filename: str
    fasta_filename: str

    def validate(self, tmp_path: Path) -> None:
        fastq_path = TEST_DATA_DIR / self.fastq_filename
        fasta_path = TEST_DATA_DIR / self.fasta_filename
        output_path = tmp_path / self.fasta_filename

        assert is_fastq(fastq_path)
        assert is_fasta(fasta_path)

        fastq_to_fasta(fastq_path, output_path)

        assert output_path.exists()

        with open(output_path, "r") as output_file:
            with open(fasta_path, "r") as fixture_file:
                output_data = output_file.read()
                fixture_data = fixture_file.read()
                assert output_data == fixture_data


fastq_to_fasta_tests = [
    FastqConversionTest("simple.fastq", "simple.fasta"),
    FastqConversionTest("spaces.fastq", "simple.fasta"),
    FastqConversionTest("special.fastq", "simple.fasta"),
]


@pytest.mark.parametrize("test", fastq_to_fasta_tests)
def test_fastq_to_fasta(test: FastqConversionTest, tmp_path: Path) -> None:
    test.validate(tmp_path)
