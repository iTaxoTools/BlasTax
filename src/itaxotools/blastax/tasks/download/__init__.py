from itaxotools.blastax.resources import task_pixmaps_large, task_pixmaps_medium

title = "Download extras"
description = "Download taxdump and taxdb"

pixmap = task_pixmaps_large.about
pixmap_medium = task_pixmaps_medium.about

long_description = (
    "Download and extract taxdump and taxdb files from NCBI: ftp://ftp.ncbi.nlm.nih.gov/ "
    "\n"
    "These files are required for taxonomy-aware BLAST operations. "
)
