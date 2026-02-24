from itaxotools.blastax.resources import task_pixmaps_large, task_pixmaps_medium

title = "Download taxonomic extras"
description = "Get taxdump and taxdb from NCBI"

pixmap = task_pixmaps_large.download
pixmap_medium = task_pixmaps_medium.download

long_description = (
    "Download and extract the latest taxdump and taxdb files from the NCBI server: ftp://ftp.ncbi.nlm.nih.gov/ "
    "\n"
    "These files are required for taxonomy-aware BLAST operations. "
)
