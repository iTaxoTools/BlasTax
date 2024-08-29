import sys
from pathlib import Path

if __name__ == "__main__":
    ROOT = Path(__file__).parent.parent
    sys.path.append(str(ROOT))

    from core import get_blast_version

    version = get_blast_version()

    version_path = ROOT / "documents" / "version.txt"

    with open(version_path, "w") as file:
        print(version, file=file)
