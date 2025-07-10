import os
import shutil

import pytest

from itaxotools.blastax.core import get_blast_env

binaries = [
    "makeblastdb",
    "blastn",
    "blastp",
    "blastx",
    "tblastn",
    "tblastx",
]

extra_binaries = [
    "windowmasker",
    "tblastn_vdb",
    "blast_vdb_cmd",
    "deltablast",
    "rpsblast",
    "blastdbcmd",
    "convert2blastmask",
    "makeprofiledb",
    "rpstblastn",
    "blastdb_aliastool",
    "segmasker",
    "blast_formatter_vdb",
    "dustmasker",
    "psiblast",
    "makembindex",
    "blast_formatter",
    "blastn_vdb",
    "blastdbcheck",
]


@pytest.mark.parametrize("binary", binaries)
def test_binaries_in_path(binary: str):
    os.environ = get_blast_env()
    for binary in binaries:
        assert shutil.which(binary)


@pytest.mark.skip(reason="Not strictly required, might have been trimmed")
@pytest.mark.parametrize("binary", extra_binaries)
def test_extra_binaries_in_path(binary: str):
    os.environ = get_blast_env()
    for binary in binaries:
        assert shutil.which(binary)
