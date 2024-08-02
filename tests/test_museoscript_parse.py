from __future__ import annotations

from pathlib import Path
from typing import NamedTuple

import pytest

from core import museoscript_parse

TEST_DATA_DIR = Path(__file__).parent / Path(__file__).stem


class MuseoTest(NamedTuple):
    blast_path: str
    output_path: str
    pident_threshold: float

    def validate(self, tmp_path: Path) -> None:
        blast_path = TEST_DATA_DIR / self.blast_path
        output_path = tmp_path / self.output_path
        print(f"Blast Path: {blast_path}")
        print(f"Output Path: {output_path}")
        museoscript_parse(
            str(blast_path),
            str(output_path),
            self.pident_threshold,
        )

        assert output_path.exists()


# New blast tests
museo_tests = [
    MuseoTest(
        "blast_output.out",
        "museoscript_output.out",
        0.9,
    ),
]


@pytest.mark.parametrize("test", museo_tests)
def test_museoscript(test: MuseoTest, tmp_path: Path) -> None:
    test.validate(TEST_DATA_DIR)
