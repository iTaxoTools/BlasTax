from __future__ import annotations

from pathlib import Path
from typing import NamedTuple

import pytest

from core import make_database, run_blast_decont

from .pytest_utils import assert_file_equals

TEST_DATA_DIR = Path(__file__).parent / Path(__file__).stem


class DecontTest(NamedTuple):
    blast_binary: str
    query_path: str
    ingroup_filename: str
    outgroup_filename: str
    blasted_ingroup_filename: str
    blasted_outgroup_filename: str
    evalue: str = "0.001"
    num_threads: int = 1

    def validate(self, tmp_path: Path) -> None:
        query_path = TEST_DATA_DIR / self.query_path
        ingroup_path = TEST_DATA_DIR / self.ingroup_filename
        outgroup_path = TEST_DATA_DIR / self.outgroup_filename
        db_ingroup_path = tmp_path / "ingroup"
        db_outgroup_path = tmp_path / "outgroup"
        blasted_ingroup_path = tmp_path / "ingroup.tsv"
        blasted_outgroup_path = tmp_path / "outgroup.tsv"

        make_database(
            input_path=ingroup_path,
            output_path=tmp_path,
            type="nucl",
            name="ingroup",
            version=4,
        )

        make_database(
            input_path=outgroup_path,
            output_path=tmp_path,
            type="nucl",
            name="outgroup",
            version=4,
        )

        run_blast_decont(
            blast_binary=self.blast_binary,
            query_path=str(query_path),
            database_path=str(db_ingroup_path),
            output_path=str(blasted_ingroup_path),
            evalue=self.evalue,
            num_threads=self.num_threads,
        )
        assert blasted_ingroup_path.exists()

        run_blast_decont(
            blast_binary=self.blast_binary,
            query_path=str(query_path),
            database_path=str(db_outgroup_path),
            output_path=str(blasted_outgroup_path),
            evalue=self.evalue,
            num_threads=self.num_threads,
        )
        assert blasted_outgroup_path.exists()

        assert_file_equals(blasted_ingroup_path, TEST_DATA_DIR / self.blasted_ingroup_filename)
        assert_file_equals(blasted_outgroup_path, TEST_DATA_DIR / self.blasted_outgroup_filename)

        print(tmp_path)

        assert False


decont_tests = [
    DecontTest(
        "blastn",
        "simple/query.fas",
        "simple/ingroup.fas",
        "simple/outgroup.fas",
        "simple/ingroup.tsv",
        "simple/outgroup.tsv",
    ),
]


@pytest.mark.parametrize("test", decont_tests)
def test_run_blast(test: DecontTest, tmp_path: Path) -> None:
    test.validate(tmp_path)
