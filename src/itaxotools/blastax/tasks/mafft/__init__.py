from itaxotools.blastax.resources import task_pixmaps_large, task_pixmaps_medium

title = "MAFFT"
description = "Multiple sequence alignment"

pixmap = task_pixmaps_large.mafft
pixmap_medium = task_pixmaps_medium.mafft

long_description = (
    "Align sequences using MAFFT, a multiple sequence alignment program. "
    "Only a selected number of strategies and options are available. "
    "\n\n"
    "Input files must be in FASTA format. "
    "Output will consist of one FASTA file per input file. "
)
