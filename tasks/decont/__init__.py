from resources import task_pixmaps_large, task_pixmaps_medium

title = "Decontaminate"
description = "Remove outlier sequences"

pixmap = task_pixmaps_large.museo
pixmap_medium = task_pixmaps_medium.museo

long_description = (
    "Given a query file and two BLAST databases (ingroup & outgroup references), "
    "search the two databases for sequence matches. "
    "Create two new sequence files in FASTA format from the hits, "
    "each containing the query sequences that are closest to each reference. "
    "Query files must be in FASTA or FASTQ format. "
    "Output will consist of two BLAST tables and two FASTA files."
)
