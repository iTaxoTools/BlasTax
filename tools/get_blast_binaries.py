from typing import Literal
from pathlib import Path
from sys import stdout

import requests
import argparse


OS = Literal["win64", "macosx", "linux"]

BLAST_URL = "https://ftp.ncbi.nlm.nih.gov/blast/executables/blast+/"

HERE = Path(__file__).parent
BIN = HERE.parent / "bin"


def human_readable_size(size):
    for unit in ["B", "KB", "MB", "GB"]:
        if size < 1000.0 or unit == "GB":
            break
        size /= 1000.0
    return f"{size:.2f} {unit}"


def get_version() -> str:
    url = BLAST_URL + "VERSION"
    try:
        response = requests.get(url)
        response.raise_for_status()
        version = response.text.strip()
        print("Retrieved latest BLAST+ version:", version)
        return version
    except requests.exceptions.RequestException as e:
        raise Exception("Cannot retrieve latest BLAST+ version") from e


def get_tarball(path: Path, version: str, os: OS = "win64") -> Path:
    tarball = f"ncbi-blast-{version}+-x64-{os}.tar.gz"
    url = BLAST_URL + version + "/" + tarball

    path.mkdir(exist_ok=True)
    target = path / tarball

    try:
        print("Requesting:", tarball)
        response = requests.get(url, stream=True)
        response.raise_for_status()

        total_size = int(response.headers.get('content-length', 0))
        block_size = 1024
        downloaded_size = 0

        print("Total tarball size:", human_readable_size(total_size))

        with open(target, 'wb') as file:
            for data in response.iter_content(chunk_size=block_size):
                file.write(data)
                downloaded_size += len(data)
                progress = (downloaded_size / total_size) * 100
                stdout.write(f"\rDownloading... {progress:.2f}%")
                stdout.flush()
            print()

        print(f"Tarball saved as: {target}")
        return target
    except requests.exceptions.RequestException as e:
        raise Exception("Cannot retrieve BLAST+ tarball") from e


def get_blast(version: str, os: OS):
    version = version or get_version()
    path = get_tarball(BIN, version, os)


def main():
    parser = argparse.ArgumentParser(description="Get the latest BLAST+ binaries")

    parser.add_argument("-s", "--os", type=str, default="win64", help="Specify target operating system")
    parser.add_argument("-v", "--version", type=str, default="", help="Download a specific version")

    args = parser.parse_args()

    get_blast(args.version, args.os)


if __name__ == "__main__":
    main()

