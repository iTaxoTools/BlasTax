from __future__ import annotations

from pathlib import Path
from typing import Literal, NamedTuple

import pytest

from core import make_database

TEST_DATA_DIR = Path(__file__).parent / Path(__file__).stem


class DatabaseTest(NamedTuple):
    input_path: str
    output_path: str
    type: Literal["nucl", "prot"]
    name: str

    def validate(self, tmp_path: Path) -> None:
        input_path = TEST_DATA_DIR / self.input_path
        fixture_path = TEST_DATA_DIR / self.output_path
        output_path = tmp_path / self.output_path
        output_path.mkdir()
        make_database(
            str(input_path),
            str(output_path),
            self.type,
            self.name,
        )
        fixture = sorted([path for path in fixture_path.iterdir()])
        output = sorted([path for path in output_path.iterdir()])
        for fix, out in zip(fixture, output):
            assert fix.name == out.name


database_tests = [
    DatabaseTest("nucleotides.fas", "nucleotides", "nucl", "nucleotides"),
]


@pytest.mark.parametrize("test", database_tests)
def test_write_pairs(test: DatabaseTest, tmp_path: Path) -> None:
    test.validate(tmp_path)
