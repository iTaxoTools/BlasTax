from resources import task_pixmaps_large, task_pixmaps_medium

title = "SCaFoSpy"
description = "Create chimerical sequences for species"

pixmap = task_pixmaps_large.scafos
pixmap_medium = task_pixmaps_medium.scafos

long_description = (
    "Given one or more sequence files, detect sequences that belong to the same species for each file. "
    "Then create chimerical sequences for each species, using one of the available strategies. "
    "Based on the original SCaFoS, a tool for Selection, Concatenation and Fusion of Sequences for phylogenomics by Roure B. et al."
    "\n\n"
    "Input files must be in FASTA, FASTQ or ALI format. "
    "Output will consist of one FASTA file per input file. "
)
