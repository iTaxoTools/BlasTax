from resources import task_pixmaps_large, task_pixmaps_medium

title = "BLAST-Align-X"
description = "Append matching nucleotides"

pixmap = task_pixmaps_large.alignx
pixmap_medium = task_pixmaps_medium.alignx

long_description = (
    "Given one or more nucleotide query files and a protein BLAST database, search the database for sequence matches. "
    "Then for each match, search the provided nucleotide file for a sequence with the same name as the protein sequence. "
    "Finally, append the matching nucleotide sequences to the original query sequences and save as a new FASTA file. "
    "Query and nucleotide files must be in FASTA format. "
    "Output will consist of two files per query: the BLAST output and a FASTA file."
)
