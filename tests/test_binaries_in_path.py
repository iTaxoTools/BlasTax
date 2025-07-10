import os
import shutil

import pytest

from itaxotools.blastax.blast import REQUIRED_BLAST_BINARIES, get_blast_env


@pytest.mark.parametrize("binary", REQUIRED_BLAST_BINARIES)
def test_binaries_in_path(binary: str):
    os.environ = get_blast_env()
    assert shutil.which(binary)
