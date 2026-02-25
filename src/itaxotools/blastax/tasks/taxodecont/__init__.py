from itaxotools.blastax.resources import task_pixmaps_large, task_pixmaps_medium

title = "Decontamination by taxonomy"
description = "Filter sequences by taxID"

pixmap = task_pixmaps_large.decont2
pixmap_medium = task_pixmaps_medium.decont2

long_description = (
    "Given a query file and a BLAST database, search the database for sequence matches "
    "and filter sequences based on the provided taxon IDs and threshold values. "
    "Query files must be in FASTA or FASTQ format."
)
