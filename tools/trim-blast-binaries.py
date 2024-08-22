from pathlib import Path

HERE = Path(__file__).parent
BIN = HERE.parent / "bin"

KEPT_BINARIES = [
    "makeblastdb",
    "blastn",
    "blastp",
    "blastx",
    "tblastn",
    "tblastx",
]

KEPT_SUFFIXES = [
    ".so",
    ".dll",
]


def main():
    for binary in BIN.iterdir():
        if binary.stem in KEPT_BINARIES:
            continue
        if binary.suffix in KEPT_SUFFIXES:
            continue
        binary.unlink()


if __name__ == "__main__":
    main()
