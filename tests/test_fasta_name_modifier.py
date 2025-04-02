from __future__ import annotations

from pathlib import Path
from typing import NamedTuple

import pytest

from core import fasta_name_modifier

TEST_DATA_DIR = Path(__file__).parent / Path(__file__).stem


class FastaNameModifierTest(NamedTuple):
    input_name: Path | str
    output_name: Path | str
    expected_output: str
    trim: bool
    add: bool
    replace: bool
    sanitize: bool
    preserve_separators: bool
    trimposition: str
    trimmaxchar: int
    renameauto: bool
    direc: str | None
    addstring: str | None
    findstring: str | None
    replacestring: str | None
    fixaliseparator: bool
    fixseqspaces: bool
    fixseqasterisks: bool

    def validate(self, tmp_path: Path) -> None:
        input_name = TEST_DATA_DIR / self.input_name
        output_name = tmp_path / self.output_name
        expected_output = TEST_DATA_DIR / self.expected_output

        fasta_name_modifier(
            input_name=str(input_name),
            output_name=str(output_name),
            trim=self.trim,
            add=self.add,
            replace=self.replace,
            sanitize=self.sanitize,
            preserve_separators=self.preserve_separators,
            trimposition=self.trimposition,
            trimmaxchar=self.trimmaxchar,
            renameauto=self.renameauto,
            direc=self.direc,
            addstring=self.addstring,
            findstring=self.findstring,
            replacestring=self.replacestring,
            fixseqspaces=self.fixseqspaces,
            fixseqasterisks=self.fixseqasterisks,
            fixaliseparator=self.fixaliseparator,
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
        "simple_output.fas",
        "simple_output_expected.fas",
        trim=True,
        add=False,
        replace=False,
        sanitize=True,
        preserve_separators=False,
        trimposition="end",
        trimmaxchar=50,
        renameauto=True,
        direc=None,
        addstring=None,
        findstring=None,
        replacestring=None,
        fixaliseparator=False,
        fixseqspaces=False,
        fixseqasterisks=False,
    ),
    FastaNameModifierTest(  # test complex case
        "FastaExample_complex_utf8.fas",
        "complex_output.fas",
        "complex_output_expected.fas",
        trim=True,
        add=False,
        replace=False,
        sanitize=True,
        preserve_separators=False,
        trimposition="end",
        trimmaxchar=50,
        renameauto=True,
        direc=None,
        addstring=None,
        findstring=None,
        replacestring=None,
        fixaliseparator=False,
        fixseqspaces=False,
        fixseqasterisks=False,
    ),
    FastaNameModifierTest(  # test special characters
        "FastaExample_special_characters.fas",
        "special_output.fas",
        "special_output_expected.fas",
        trim=True,
        add=False,
        replace=False,
        sanitize=True,
        preserve_separators=False,
        trimposition="end",
        trimmaxchar=50,
        renameauto=True,
        direc=None,
        addstring=None,
        findstring=None,
        replacestring=None,
        fixaliseparator=False,
        fixseqspaces=False,
        fixseqasterisks=False,
    ),
    FastaNameModifierTest(  # test trim and add
        "FastaExample_simple.fas",
        "simple_output_trim_add.fas",
        "simple_output_trim_add_expected.fas",
        trim=True,
        add=True,
        replace=False,
        sanitize=True,
        preserve_separators=False,
        trimposition="end",
        trimmaxchar=50,
        renameauto=True,
        direc="end",
        addstring="end",
        findstring=None,
        replacestring=None,
        fixaliseparator=False,
        fixseqspaces=False,
        fixseqasterisks=False,
    ),
    FastaNameModifierTest(  # autoincreament without trimming
        "FastaExample_complex3.fas",
        "complex_output_auto_notrim.fas",
        "complex_output_auto_notrim_expected.fas",
        trim=False,
        add=False,
        replace=False,
        sanitize=False,
        preserve_separators=False,
        trimposition="",
        trimmaxchar=0,
        renameauto=True,
        direc=None,
        addstring=None,
        findstring=None,
        replacestring=None,
        fixaliseparator=False,
        fixseqspaces=False,
        fixseqasterisks=False,
    ),
    FastaNameModifierTest(  # sanitizing, trimming, auto, add (_) at the beginning
        "FastaExample_complex3.fas",
        "complex_output_auto_trim_san_add_beginning.fas",
        "complex_output_auto_trim_san_add_beginning_expected.fas",
        trim=True,
        add=True,
        replace=False,
        sanitize=True,
        preserve_separators=False,
        trimposition="end",
        trimmaxchar=50,
        renameauto=True,
        direc="beginning",
        addstring="_",
        findstring=None,
        replacestring=None,
        fixaliseparator=False,
        fixseqspaces=False,
        fixseqasterisks=False,
    ),
    FastaNameModifierTest(  # ali parsing
        "ali_simple.ali",
        "ali_simple_out.fas",
        "ali_simple_expected.fas",
        trim=False,
        add=False,
        replace=False,
        sanitize=True,
        preserve_separators=True,
        trimposition="",
        trimmaxchar=0,
        renameauto=False,
        direc=None,
        addstring=None,
        findstring=None,
        replacestring=None,
        fixaliseparator=True,
        fixseqspaces=True,
        fixseqasterisks=True,
    ),
    FastaNameModifierTest(  # test replace
        "FastaExample_simple.fas",
        "replace_output.fas",
        "replace_output_expected.fas",
        trim=False,
        add=False,
        replace=True,
        sanitize=False,
        preserve_separators=False,
        trimposition=None,
        trimmaxchar=None,
        renameauto=None,
        direc=None,
        addstring=None,
        findstring="MVTIS",
        replacestring="ISMTV",
        fixaliseparator=False,
        fixseqspaces=False,
        fixseqasterisks=False,
    ),
]

@pytest.mark.parametrize("test", fasta_name_modifier_tests)
def test_fasta_modifier(test: FastaNameModifierTest, tmp_path: Path) -> None:
    test.validate(tmp_path)
