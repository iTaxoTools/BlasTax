from itaxotools.blastax.resources import task_pixmaps_large, task_pixmaps_medium

title = "Assign BLAST taxonomy"
description = "Identify taxid and organism"

pixmap = task_pixmaps_large.about
pixmap_medium = task_pixmaps_medium.about

long_description = (
    "Given one or more query files and a BLAST database, search the database for sequence matches "
    "and assign taxonomic information to each query sequence based on the best hit. "
    "Query files must be in FASTA or FASTQ format. "
    "Output will consist of two files per query: the BLAST output and an annotated FASTA file."
)
