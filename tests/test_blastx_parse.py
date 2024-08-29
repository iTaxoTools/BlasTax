from __future__ import annotations

from pathlib import Path
from typing import NamedTuple

import pytest

from core import blastx_parse

TEST_DATA_DIR = Path(__file__).parent / Path(__file__).stem


class BlastxParseTest(NamedTuple):
    input_path: Path | str
    blast_result_path: Path | str
    output_path: Path | str
    extra_nucleotide_path: Path | str
    database_name: str
    expected_output: str

    def validate(self, tmp_path: Path) -> None:
        input_path = TEST_DATA_DIR / self.input_path
        blast_result_path = TEST_DATA_DIR / self.blast_result_path
        output_path = tmp_path / self.output_path
        database_name = self.database_name
        extra_nucleotide_path = TEST_DATA_DIR / self.extra_nucleotide_path
        expected_output = TEST_DATA_DIR / self.expected_output
        blastx_parse(
            str(input_path), str(blast_result_path), str(output_path), str(extra_nucleotide_path), str(database_name)
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
blastx_parse_tests = [
    BlastxParseTest(
        "2gene1_nucleotides_query.fas",
        "2gene1_nucleotides_query.out",
        "2gene1_nucleotides_query_blastmatchesadded.fas",
        "2transcript_assembly_nucleotides.fas",
        "blastx_db",
        "2gene1_nucleotides_query_expected.fas",
    ),
]


@pytest.mark.parametrize("test", blastx_parse_tests)
def test_museoscript(test: BlastxParseTest, tmp_path: Path) -> None:
    test.validate(tmp_path)
