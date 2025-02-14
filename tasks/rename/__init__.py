from resources import task_pixmaps_large, task_pixmaps_medium

title = "FastPrepare"
description = "Rename sequence identifiers"

pixmap = task_pixmaps_large.rename
pixmap_medium = task_pixmaps_medium.rename

long_description = (
    "Given one or more FASTA or ALI files, rename all sequence identifiers "
    "and save the modified files in FASTA format. \n"
    "The default options are suitable for preparing sequence files for BLAST analysis. "
)
