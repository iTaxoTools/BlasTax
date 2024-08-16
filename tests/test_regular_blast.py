from __future__ import annotations

from pathlib import Path
from typing import NamedTuple

import pytest

from core import run_blast

TEST_DATA_DIR = Path(__file__).parent / Path(__file__).stem


class BlastTest(NamedTuple):
    blast_binary: str
    query_path: str
    database_path: str
    output_path: str
    evalue: str
    num_threads: int
    outfmt: str
    other: str
    blast_expected: str

    def validate(self, tmp_path: Path) -> None:
        query_path = TEST_DATA_DIR / self.query_path
        database_path = TEST_DATA_DIR / self.database_path
        output_path = tmp_path / self.output_path
        blast_expected = TEST_DATA_DIR / self.blast_expected

        run_blast(
            self.blast_binary,
            str(query_path),
            str(database_path),
            str(output_path),
            self.evalue,
            self.num_threads,
            self.outfmt,
            self.other,
        )
        assert output_path.exists()

        # Verify that the output matches the expected output
        with open(output_path, "r") as output_file:
            output_data = output_file.read()

        with open(blast_expected, "r") as expected_file:
            expected_data = expected_file.read()

        assert output_data == expected_data
        print("Output matches expected output.")


# New blast tests
blast_tests = [
    BlastTest("blastn", "malamini.fas", "mala.fas", "blast_output.txt", "0.001", 1, "1", "", "blast_expected.out"),
    BlastTest("blastn", "HI.4019.002.index_7.ANN0831_R1_small.fastq", "HI.4019.002.index_7.ANN0831_R1_mod", "blast_output_fastq.txt", "0.001", 1, "6 qseqid sseqid sacc stitle pident qseq", "", "blast_output_fastq_expected.out"),
]


@pytest.mark.parametrize("test", blast_tests)
def test_run_blast(test: BlastTest, tmp_path: Path) -> None:
    test.validate(tmp_path)
