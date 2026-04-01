#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""Update README.md version strings before a release"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent


def update_readme(version: str) -> None:
    readme = ROOT / "README.md"
    content = readme.read_text(encoding="utf-8")
    content = re.sub(r"BlasTax_\d+\.\d+\.\d+", f"BlasTax_{version}", content)
    content = re.sub(r"BlasTax-\d+\.\d+\.\d+", f"BlasTax-{version}", content)
    content = re.sub(r"v\d+\.\d+\.\d+", f"v{version}", content)
    readme.write_text(content, encoding="utf-8")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: python {Path(__file__).name} <version>")
        print(f"Example: python {Path(__file__).name} 0.2.0")
        sys.exit(1)

    version = sys.argv[1]
    if not re.fullmatch(r"\d+\.\d+\.\d+", version):
        print(f"Error: expected version like 0.2.0, got {version!r}")
        sys.exit(1)

    update_readme(version)
    print(f"Updated README.md: BlasTax v{version}")
