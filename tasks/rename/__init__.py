from resources import task_pixmaps_large, task_pixmaps_medium

title = "FastaSeqRename"
description = "Rename FASTA identifiers"

pixmap = task_pixmaps_large.rename
pixmap_medium = task_pixmaps_medium.rename

long_description = (
    "Given one or more FASTA files, rename all sequence identifiers "
    "and save the modified files. \n"
    "Suitable for preparing FASTA files for BLAST analysis. "
)
