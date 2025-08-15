from itaxotools.blastax.resources import task_pixmaps_large, task_pixmaps_medium

title = "Codon-aware alignment"
description = "Align via proteins without altering codons"

pixmap = task_pixmaps_large.codon_align
pixmap_medium = task_pixmaps_medium.codon_align

long_description = (
    "Performs codon-aware alignment by translating nucleotides to proteins, aligning using MAFFTpy,"
    "then restoring the original nucleotide sequence for accurate downstream analysis. "
    "\n\n"
    "Input files must be in FASTA format. "
    "Output will consist of one FASTA file per input file. "
)
