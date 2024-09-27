from __future__ import annotations

from pathlib import Path
from typing import NamedTuple

import pytest

from core import blast_parse

TEST_DATA_DIR = Path(__file__).parent / Path(__file__).stem


class BlastnParseTest(NamedTuple):
    input_path: Path | str
    blast_result_path: Path | str
    output_path: Path | str
    database_name: str
    all_matches: bool
    pident: float
    length: int
    user_spec_name: str
    expected_output: str

    def validate(self, tmp_path: Path) -> None:
        input_path = TEST_DATA_DIR / self.input_path
        blast_result_path = TEST_DATA_DIR / self.blast_result_path
        output_path = tmp_path / self.output_path
        database_name = self.database_name
        all_matches = self.all_matches
        pident = self.pident
        length = self.length
        user_spec_name = self.user_spec_name
        expected_output = TEST_DATA_DIR / self.expected_output
        blast_parse(
            str(input_path), str(blast_result_path), str(output_path), str(database_name), all_matches, pident, length, user_spec_name
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
blastn_parse_tests = [
    BlastnParseTest(  # test blastn
        "blastn/Salamandra_testqueryfile.fas",
        "blastn/Salamandra_testqueryfile.out",
        "Salamandra_blastmatchesadded.out",
        "salamandra_db",
        False,
        None,
        None,
        None,
        "blastn/Salamandra_testqueryfile_expected.fas",
    ),
    BlastnParseTest(  # test blastp
        "blastp/proteins.fasta",
        "blastp/blastp_expected.out",
        "proteins_blastmatchesadded.out",
        "sequence_db",
        False,
        None,
        None,
        None,
        "blastp/proteins_blastmatchesadded_expected.out",
    ),
BlastnParseTest(  # test tblastx
        "tblastx/malamini.fas",
        "tblastx/tblastx_expected.out",
        "tblastx_blastmatchesadded.out",
        "mala_db",
        False,
        None,
        None,
        None,
        "tblastx/tblastx_blastmatchesadded_expected.out",
    ),
    BlastnParseTest(  # Include all matches
        "blastn/Salamandra_testqueryfile.fas",
        "blastn/Salamandra_testqueryfile.out",
        "Salamandra_blastmatchesadded_all_matches.out",
        "salamandra_db",
        True,
        None,
        None,
        None,
        "blastn/Salamandra_blastmatchesadded_expected_all_matches.out",
    ),
    BlastnParseTest(  # test trinity name fixing
        "trinity_fix/6458_Query.fasta",
        "trinity_fix/blastn_Chlorococcum_output.txt",
        "6458_blastmatchesadded_fixed.out",
        "",
        False,
        None,
        None,
        "shared_name",
        "trinity_fix/6458_expected.out",
    ),

]


@pytest.mark.parametrize("test", blastn_parse_tests)
def test_blast_parse(test: BlastnParseTest, tmp_path: Path) -> None:
    test.validate(tmp_path)
