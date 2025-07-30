from itaxotools.blastax.resources import task_pixmaps_large, task_pixmaps_medium

title = "Removal of stop codons"
description = "Remove stop codons from a dataset"

pixmap = task_pixmaps_large.removal
pixmap_medium = task_pixmaps_medium.removal

long_description = (
    "Scan the given FASTA files for sequences containing stop codons. "
    "Then rewrite the dataset with the detected stop codons removed, "
    "using the selected method."
)
