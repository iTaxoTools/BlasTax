from resources import task_pixmaps_large, task_pixmaps_medium

title = "BLAST-Align"
description = "Add matching sequences to alignment"

pixmap = task_pixmaps_large.align
pixmap_medium = task_pixmaps_medium.align

long_description = (
    "Given one or more query file(s) and a BLAST database, search the database for sequence matches, "
    "then concatenate the original sequences and their matches into a new file. "
    "The query file(s) must be in FASTA format. "
    "Output will consist of two files per query: the BLAST output and a FASTA file."
)
