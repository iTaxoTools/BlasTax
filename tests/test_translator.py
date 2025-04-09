from __future__ import annotations

from pathlib import Path
from typing import Literal, NamedTuple

import pytest

from translator import Options, translate

TEST_DATA_DIR = Path(__file__).parent / Path(__file__).stem


class TranslatorTest(NamedTuple):
    input_filename: str
    output_filename: str
    nucleotide_filename: str | None
    log_filename: str | None

    input_type: Literal["cds", "cds_stop", "transcript ", "all"]
    frame: Literal["autodetect", "1", "2", "3", "4", "5", "6"]
    code: str | int


    def validate(self, tmp_path: Path) -> None:
        input_path = TEST_DATA_DIR / self.input_filename
        output_expected = TEST_DATA_DIR / self.output_filename
        output_path = tmp_path / self.output_filename
        nucleotide_expected = None
        nucleotide_path = None
        log_expected = None
        log_path = None

        if self.nucleotide_filename is not None:
            nucleotide_expected = TEST_DATA_DIR / self.nucleotide_filename
            log_path = tmp_path / self.nucleotide_filename

        if self.log_filename is not None:
            log_expected = TEST_DATA_DIR / self.log_filename
            log_path = tmp_path / self.log_filename

        options = Options(
            input_path=input_path,
            output_path=output_path,
            log_path=log_path,
            nucleotide_path=nucleotide_path,
            input_type=self.input_type,
            frame=self.frame,
            code=self.code,
        )

        translate(options)

        for output, expected in [
            (output_path, output_expected),
            (nucleotide_path, nucleotide_expected),
            (log_path, log_expected),
        ]:
            if output is None:
                continue

            assert output.exists()

            with open(output, "r") as output_file:
                output_data = output_file.read()

            with open(expected, "r") as expected_file:
                expected_data = expected_file.read()

            assert output_data == expected_data


translator_tests = [
    TranslatorTest(
        "translator_testfile.fas",
        "translator_testfile_aa_expected_codonmode.fas",
        None, None, "cds_stop", "autodetect", 1,
    ),
    TranslatorTest(
        "translator_testfile.fas",
        "translator_testfile_aa_expected_transcriptmode.fas",
        "translator_testfile__orf_nt_expected_transcriptmode.fas",
        None, "transcript", "autodetect", 1,
    ),
]


@pytest.mark.parametrize("test", translator_tests)
def test_run_translator(test: TranslatorTest, tmp_path: Path) -> None:
    test.validate(tmp_path)
