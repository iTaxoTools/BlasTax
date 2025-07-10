from __future__ import annotations

from pathlib import Path
from typing import NamedTuple

import pytest

from itaxotools.blastax.core import museoscript_parse

TEST_DATA_DIR = Path(__file__).parent / Path(__file__).stem


class MuseoTest(NamedTuple):
    blast_path: str
    output_path: str
    pident_threshold: float
    expected_output: str

    def validate(self, tmp_path: Path) -> None:
        blast_path = TEST_DATA_DIR / self.blast_path
        output_path = tmp_path / self.output_path
        expected_output = TEST_DATA_DIR / self.expected_output
        print(f"Blast Path: {blast_path}")
        print(f"Output Path: {output_path}")
        museoscript_parse(
            str(blast_path),
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
museo_tests = [
    MuseoTest("blast_output.out", "museoscript_output.out", 0.9, "museoscript_expected.out"),
]


@pytest.mark.parametrize("test", museo_tests)
def test_museoscript(test: MuseoTest, tmp_path: Path) -> None:
    test.validate(tmp_path)
