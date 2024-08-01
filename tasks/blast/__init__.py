from resources import task_pixmaps_large, task_pixmaps_medium

title = "Regular BLAST"
description = "Calculate statistical significance"

pixmap = task_pixmaps_large.blast
pixmap_medium = task_pixmaps_medium.blast

long_description = (
    "Find regions of similarity between sequences in the query file "
    "and sequences in a BLAST database. "
    "Query files must be in FASTA format. "
)
