from resources import task_pixmaps_large, task_pixmaps_medium

title = "Museoscript"
description = "Save matches as FASTA"

pixmap = task_pixmaps_large.museo
pixmap_medium = task_pixmaps_medium.museo

long_description = (
    "Given a nucleotide query file and a nucleotide BLAST database, "
    "search the database for sequence matches, then create a sequence file "
    "in FASTA format from the hits. "
    "Query files must be in FASTA or FASTQ format. "
    "Output will consist of two files per query: the BLAST output and a FASTA file."
)
