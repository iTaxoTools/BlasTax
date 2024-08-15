'''
from __future__ import annotations



from pathlib import Path
from typing import Literal, NamedTuple

import pytest

from core import fastq_to_fasta

TEST_DATA_DIR = Path(__file__).parent / Path(__file__).stem

class FastqToFasta(NamedTuple):
    fastq_path: str
    output_path: str
    expected_output: str

    def validate(self, tmp_path: Path) -> None:
       fastq_path = TEST_DATA_DIR / self.fastq_path
       output_path = TEST_DATA_DIR / self.output_path
       expected_output = TEST_DATA_DIR / self.expected_output

       fastq_to_fasta(
            str(fastq_path),
            str(output_path),
        )

       assert output_path.exists()

       # Verify that the output matches the expected output
       with open(output_path, 'r') as output_file:
           output_data = output_file.read()

       with open(expected_output, 'r') as expected_file:
           expected_data = expected_file.read()

       assert output_data == expected_data
       print(f"Output matches expected output.")


# New blast tests
FastqToFasta_test = [
    FastqToFasta(
        "HI.4019.002.index_7.ANN0831_R1.fastq",
        "HI.4019.002.index_7.ANN0831_R1.fasta",
        "HI.4019.002.index_7.ANN0831_R1_expected.fasta",
    ),
]

@pytest.mark.parametrize("test", FastqToFasta_test)
def test_fastq_to_fasta(test: FastqToFasta, tmp_path: Path) -> None:
    test.validate(TEST_DATA_DIR)
'''