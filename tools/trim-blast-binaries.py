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
    count = 0
    for binary in BIN.iterdir():
        if binary.stem in KEPT_BINARIES:
            continue
        if binary.suffix in KEPT_SUFFIXES:
            continue
        binary.unlink()
        count += 1
    print(f"Trimmed {count} binaries!")


if __name__ == "__main__":
    main()
