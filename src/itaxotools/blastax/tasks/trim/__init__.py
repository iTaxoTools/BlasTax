from itaxotools.blastax.resources import task_pixmaps_large, task_pixmaps_medium

title = "Codon trimming"
description = "Trim sequences by stop codons"

pixmap = task_pixmaps_large.trim
pixmap_medium = task_pixmaps_medium.trim

long_description = (
    "Automatically determine the optimal reading frame for each sequence "
    "by minimizing the number of stop codons. Then trim each sequence "
    "at the beginning to ensure it starts at the first codon position."
)
