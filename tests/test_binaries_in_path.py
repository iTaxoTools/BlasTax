import shutil
import os

import pytest

import core


binaries = [
    "windowmasker",
    "makeblastdb",
    "blastp",
    "tblastn_vdb",
    "blast_vdb_cmd",
    "blastx",
    "deltablast",
    "rpsblast",
    "blastdbcmd",
    "tblastx",
    "convert2blastmask",
    "makeprofiledb",
    "rpstblastn",
    "blastdb_aliastool",
    "segmasker",
    "blast_formatter_vdb",
    "dustmasker",
    "blastn",
    "psiblast",
    "makembindex",
    "blast_formatter",
    "blastn_vdb",
    "tblastn",
    "blastdbcheck",
]

@pytest.mark.parametrize("binary", binaries)
def test_binaries_in_path(binary: str):
    os.environ = core.get_blast_env()
    for binary in binaries:
        assert shutil.which(binary)
