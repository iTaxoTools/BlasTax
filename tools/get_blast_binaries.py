from typing import Literal
from pathlib import Path
from sys import stdout
from platform import system

import requests
import argparse
import tempfile
import tarfile
import shutil


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


def find_subdirectory(start_path: Path, name: str) -> Path | None:
    for path in start_path.rglob('*'):
        if path.is_dir() and path.name == name:
            return path
    return None


def get_os_extensions(os: OS) -> list[str]:
    if os == "win64":
        return [".exe", ".dll"]
    elif os == "macosx":
        return [""]
    raise Exception(f"Unknown binary extensions for os: {os}")


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


def get_system_os() -> OS:
    this = system()
    if this == "Linux":
        return "linux"
    elif this == "Windows":
        return "win64"
    elif this == "Darwin":
        return "macosx"
    raise Exception(f"Unknown os: {this}")


def get_architecture(os: OS) -> str:
    if os == "macosx":
        return "universal"
    return "x64"


def get_tarball(path: Path, version: str, os: OS = "win64", arch: str = "x64") -> Path:
    tarball = f"ncbi-blast-{version}+-{arch}-{os}.tar.gz"
    url = BLAST_URL + version + "/" + tarball

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


def extract_tarball(tarball_path: Path, target_path: Path) -> Path:
    try:
        with tarfile.open(tarball_path, 'r:gz') as tar:
            tar.extractall(path=target_path)
        print(f"Extracted tarball to: {target_path}")

    except tarfile.TarError as e:
        raise Exception(f"Error extracting: {e}") from e

    bin = find_subdirectory(target_path, "bin")
    if not bin:
        raise Exception("Cannot detect bin subdirectory")
    return bin


def copy_binaries(src: Path, dst: Path, extensions: list[str]):
    count = 0
    for file in src.iterdir():
        if file.suffix in extensions:
            shutil.copy(file, dst)
            count += 1
    print(f"Copied {count} binaries to: {dst}")


def get_blast(version: str, os: str):
    version = version or get_version()
    os = os or get_system_os()
    arch = get_architecture(os)

    with tempfile.TemporaryDirectory() as work_dir:
        work_path = Path(work_dir)
        path = get_tarball(work_path, version, os, arch)
        bin = extract_tarball(path, work_path)
        extensions = get_os_extensions(os)

        BIN.mkdir(exist_ok=True)
        copy_binaries(bin, BIN, extensions)

    print("Done!")


def main():
    parser = argparse.ArgumentParser(description="Get the latest BLAST+ binaries")

    parser.add_argument("-v", "--version", type=str, default="", help="Download a specific version")
    parser.add_argument("-s", "--os", type=str, default="", help="Specify target operating system")

    args = parser.parse_args()

    get_blast(args.version, args.os)


if __name__ == "__main__":
    main()

