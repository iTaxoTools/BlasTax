from itaxotools.blastax.resources import task_pixmaps_large, task_pixmaps_medium

title = "Group merge"
description = "Merge FASTA files by filename"

pixmap = task_pixmaps_large.groupmerge
pixmap_medium = task_pixmaps_medium.groupmerge

long_description = (
    "Given a folder containing multiple FASTA sequence files, match files "
    "into groups based on their filenames. "
    "\n"
    "Then merge all sequences of each group into a single FASTA file. "
)
