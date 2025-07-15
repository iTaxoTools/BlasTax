#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""Launch the Hapsolutely GUI"""

import multiprocessing
import os
import sys
from pathlib import Path

from itaxotools.blastax import run

if __name__ == "__main__":
    multiprocessing.freeze_support()

    if hasattr(sys, "_MEIPASS"):
        blast_path = Path(sys._MEIPASS) / "bin"
        os.environ["PATH"] += f"{os.pathsep}{blast_path}"

    run()
