from itaxotools.blastax.resources import task_pixmaps_large, task_pixmaps_medium

title = "Cutadapt"
description = "Remove adapter sequences"

pixmap = task_pixmaps_large.cutadapt
pixmap_medium = task_pixmaps_medium.cutadapt

long_description = (
    "Find and remove adapter sequences, primers, poly-A tails and other types "
    "of unwanted sequence from your high-throughput sequencing reads. "
    "Sequence files must be in FASTA or FASTQ format. "
)
