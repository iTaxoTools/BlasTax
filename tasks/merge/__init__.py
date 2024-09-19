from resources import task_pixmaps_large, task_pixmaps_medium

title = "FastaMerge"
description = "Merge FASTA files"

pixmap = task_pixmaps_large.merge
pixmap_medium = task_pixmaps_medium.merge

long_description = (
    "Given a folder containing multiple FASTA sequence files, match files "
    "into groups based on their filenames. "
    "\n"
    "Then merge all sequences of each group into a single FASTA file. "
)
