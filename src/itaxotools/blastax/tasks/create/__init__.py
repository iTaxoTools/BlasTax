from itaxotools.blastax.resources import task_pixmaps_large, task_pixmaps_medium

title = "Make BLAST database"
description = "Created from FASTA sequences"

pixmap = task_pixmaps_large.create
pixmap_medium = task_pixmaps_medium.create

long_description = (
    "Turn sequences into a BLAST database, which can then be used in downstream analysis. "
    "Input must be in FASTA format. Output will be a BLAST database (version 4), "
    "which consists of multiple files. "
)
