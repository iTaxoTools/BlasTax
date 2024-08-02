from __future__ import annotations

from pathlib import Path
from typing import NamedTuple

import pytest

from core import run_blast

TEST_DATA_DIR = Path(__file__).parent / Path(__file__).stem
# TEST_DATA_DIR = Path(__file__).parent / "test_data"


class BlastTest(NamedTuple):
    blast_binary: str
    query_path: str
    database_path: str
    output_path: str
    evalue: str
    num_threads: int
    outfmt: str
    other: str

    def validate(self, tmp_path: Path) -> None:
        query_path = TEST_DATA_DIR / self.query_path
        database_path = TEST_DATA_DIR / self.database_path
        output_path = tmp_path / self.output_path
        assert run_blast(
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


# New blast tests
blast_tests = [
    BlastTest(
        "blastn",
        "malamini.fas",
        "mala.fas",
        "blast_output.txt",
        "0.001",
        1,
        "1",
        "",
    ),
]


@pytest.mark.parametrize("test", blast_tests)
def test_run_blast(test: BlastTest, tmp_path: Path) -> None:
    # output_dir = TEST_DATA_DIR / "blast_output"
    #    output_dir.mkdir(exist_ok=True)
    test.validate(TEST_DATA_DIR)


#    test.validate(tmp_path)
