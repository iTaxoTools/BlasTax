from itaxotools.blastax.resources import task_pixmaps_large, task_pixmaps_medium

title = "Download NCBI databases"
description = "Get the latest taxDump and taxDB"

pixmap = task_pixmaps_large.download
pixmap_medium = task_pixmaps_medium.download

long_description = (
    "Download and extract the latest taxDump and taxDB files from the NCBI server: ftp://ftp.ncbi.nlm.nih.gov/ "
    "\n"
    "These files are required for taxonomy-aware BLAST operations. "
)
