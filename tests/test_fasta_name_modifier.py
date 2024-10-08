from __future__ import annotations

from pathlib import Path
from typing import NamedTuple

import pytest

from core import fasta_name_modifier

TEST_DATA_DIR = Path(__file__).parent / Path(__file__).stem


class FastaNameModifierTest(NamedTuple):
    input_name: Path | str
    output_name: Path | str
    trim: bool
    add: bool
    sanitize: bool
    trimposition: str
    trimmaxchar: int
    renameauto: bool
    expected_output: str
    direc: str = None
    addstring: str = None

    def validate(self, tmp_path: Path) -> None:
        input_name = TEST_DATA_DIR / self.input_name
        output_name = tmp_path / self.output_name
        trim = self.trim
        add = self.add
        sanitize = self.sanitize
        trimposition = self.trimposition
        trimmaxchar = self.trimmaxchar
        renameauto = self.renameauto
        direc = self.direc
        addstring = self.addstring
        expected_output = TEST_DATA_DIR / self.expected_output

        fasta_name_modifier(
            str(input_name),
            str(output_name),
            trim,
            add,
            sanitize,
            str(trimposition),
            int(trimmaxchar),
            renameauto,
            direc,
            addstring
        )

        assert output_name.exists()

        # Verify that the output matches the expected output
        with open(output_name, "r", encoding="utf-8", errors="surrogateescape") as output_file:
            output_data = output_file.read()

        with open(expected_output, "r", encoding="utf-8", errors="surrogateescape") as expected_file:
            expected_data = expected_file.read()

        assert output_data == expected_data
        print("Output matches expected output.")


# New blast tests
fasta_name_modifier_tests = [
    FastaNameModifierTest(  # test simple case
        "FastaExample_simple.fas",
        "simlpe_output.fas",
        True,
        False,
        True,
        "end",
        50,
        True,
        #        None,
        #        None,
        "simlpe_output_expected.fas",
    ),
    FastaNameModifierTest(  # test complex case
        "FastaExample_complex_utf8.fas",
        "complex_output.fas",
        True,
        False,
        True,
        "end",
        50,
        True,
        #        None,
        #        None,
        "complex_output_expected.fas",
    ),
    FastaNameModifierTest(  # test special characters
        "FastaExample_special_characters.fas",
        "special_output.fas",
        True,
        False,
        True,
        "end",
        50,
        True,
#        None,
#        None,
        "special_output_expected.fas",
    ),
    FastaNameModifierTest(  # test trim and add
        "FastaExample_simple.fas",
        "simlpe_output_trim_add.fas",
        True,
        True,
        True,
        "end",
        50,
        True,
#        "Beginning",
#        "Beginning",
        "simlpe_output_trim_add_expected.fas",
         "end",
        "end",
    ),
    FastaNameModifierTest(  # autoincreament without trimming
        "FastaExample_complex3.fas",
        "complex_output_auto_notrim.fas",
        False,
        False,
        False,
        "",
        0,
        True,
#        "Beginning",
#        "Beginning",
        "complex_output_auto_notrim_expected.fas",
    ),
    FastaNameModifierTest(  # sanitizing, trimming, auto, add (_) at the beginning
        "FastaExample_complex3.fas",
        "complex_output_auto_trim_san_add_beginning.fas",
        True,
        True,
        True,
        "end",
        50,
        True,
        "complex_output_auto_trim_san_add_beginning_expected.fas",
        "beginning",
        "_",
    ),
]

@pytest.mark.parametrize("test", fasta_name_modifier_tests)
def test_fasta_modifier(test: FastaNameModifierTest, tmp_path: Path) -> None:
    test.validate(tmp_path)
