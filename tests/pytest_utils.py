from pathlib import Path


def assert_file_equals(output_path: Path | str, expected_path: Path | str):
    with open(output_path, "r") as output_file:
        with open(expected_path, "r") as expected_file:
            output_data = output_file.read()
            expected_data = expected_file.read()
            assert output_data == expected_data
