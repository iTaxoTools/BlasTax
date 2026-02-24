from itaxotools.blastax.resources import task_pixmaps_large, task_pixmaps_medium

title = "Taxonomic decontamination"
description = "Filter sequences by taxonomy"

pixmap = task_pixmaps_large.decont
pixmap_medium = task_pixmaps_medium.decont

long_description = (
    "Given a query file and a BLAST database, search the database for sequence matches "
    "and filter sequences based on the provided threshold values. "
    "Query files must be in FASTA or FASTQ format."
)
