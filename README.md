# BlasTax

[![GitHub - Tests](https://img.shields.io/github/actions/workflow/status/iTaxoTools/BlasTax/test.yml?label=tests)](
    https://github.com/iTaxoTools/BlasTax/actions/workflows/test.yml)
[![GitHub - Windows](https://img.shields.io/github/actions/workflow/status/iTaxoTools/BlasTax/windows.yml?label=windows)](
    https://github.com/iTaxoTools/BlasTax/actions/workflows/windows.yml)
[![GitHub - macOS](https://img.shields.io/github/actions/workflow/status/iTaxoTools/BlasTax/macos.yml?label=macos)](
    https://github.com/iTaxoTools/BlasTax/actions/workflows/macos.yml)

**WORK IN PROGRESS**

A graphical user interface to run BLAST and parse hits.

- **Make BLAST database**: Create a BLAST database from a sequence file
- **Regular BLAST**: Find regions of similarity between sequences in a query file and a BLAST database
- **BLAST-Append**: Append the aligned part of matching sequences to the original query sequences
- **BLAST-Append-X**: Like BLAST-Append, but appends nucleotides c orresponding to the protein database
- **Decontaminate**: Remove contaminants from query sequences based on two ingroup and outgroup databases
- **Museoscript**: Create sequence files from BLAST matches

The program also includes a variety of tools for processing FASTA files.

- **Fast prepare**: Rename FASTA sequence identifiers in preparation for BLAST analysis
- **Fast split**: Split large sequences or text files into smaller files
- **Fast merge**: Merge multiple sequences or text files into a single large file
- **Group merge**: Merge FASTA files by filename
- **Stop codon removal**: Remove stop codons from a dataset
- **Codon trimming**: Trim coding sequences to start with first codon position

- **SCaFoSpy**: Create chimerical sequences for species
- **Protein translator**: Generate protein translations for each sequence

Input sequences must be in the FASTA or FASTQ file formats.

![Screenshot](https://raw.githubusercontent.com/iTaxoTools/BlasTax/main/images/screenshot.png)

## Executables

Download and run the standalone executables without installing Python or BLAST+.

[![Pre-release](https://img.shields.io/badge/pre--release-BlasTax_0.0.1-red?style=for-the-badge)](
    https://github.com/iTaxoTools/BlasTax/releases/latest)
[![Windows](https://img.shields.io/badge/Windows-blue.svg?style=for-the-badge&logo=data:image/svg+xml;base64,PD94bWwgdmVyc2lvbj0iMS4wIiBlbmNvZGluZz0iVVRGLTgiPz4KPCEtLSBDcmVhdGVkIHdpdGggSW5rc2NhcGUgKGh0dHA6Ly93d3cuaW5rc2NhcGUub3JnLykgLS0+Cjxzdmcgd2lkdGg9IjQ4IiBoZWlnaHQ9IjQ4IiB2ZXJzaW9uPSIxLjEiIHZpZXdCb3g9IjAgMCAxMi43IDEyLjciIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CiA8ZyBmaWxsPSIjZmZmIiBzdHJva2UtbGluZWNhcD0ic3F1YXJlIiBzdHJva2Utd2lkdGg9IjMuMTc0OSI+CiAgPHJlY3QgeD0iLjc5MzczIiB5PSIuNzkzNzMiIHdpZHRoPSI1LjAyNyIgaGVpZ2h0PSI1LjAyNyIvPgogIDxyZWN0IHg9IjcuMTQzNiIgeT0iLjc5MzczIiB3aWR0aD0iNC43NjI0IiBoZWlnaHQ9IjUuMDI3Ii8+CiAgPHJlY3QgeD0iLjc5MzczIiB5PSI2Ljg3OSIgd2lkdGg9IjUuMDI3IiBoZWlnaHQ9IjUuMDI3Ii8+CiAgPHJlY3QgeD0iNy4xNDM2IiB5PSI2Ljg3OSIgd2lkdGg9IjQuNzYyNCIgaGVpZ2h0PSI1LjAyNyIvPgogPC9nPgo8L3N2Zz4K)](
    https://github.com/iTaxoTools/BlasTax/releases/latest)
[![MacOS](https://img.shields.io/badge/macOS-slategray.svg?style=for-the-badge&logo=apple)](
    https://github.com/iTaxoTools/BlasTax/releases/latest)

## Running from source

First clone the repository and install the module.

```
git clone https://github.com/iTaxoTools/BlasTax.git
pip install BlasTax
```

You need to provide the BLAST+ binaries and add them to the system PATH before running the program.
You can use the provided submodule for downloading the binaries:
```
python -m itaxotools.blastax.download --trim
```

Adding them to PATH is OS specific. We are working on a way to bypass this step.

Run BlasTax from the command line using:

```
blastax
```

## Citations

*BlasTax* was developed in the framework of the *iTaxoTools* project:

> *Vences M. et al. (2021): iTaxoTools 0.1: Kickstarting a specimen-based software toolkit for taxonomists. - Megataxa 6: 77-92.*

Code by Nikita Kulikov, Anja-Kristina Schulz and Stefanos Patmanidis.

BlasTax integrates the BLAST+ suite from NCBI:

> *Camacho, C., Coulouris, G., Avagyan, V., Ma, N., Papadopoulos, J., Bealer, K., and Madden, T.L. 2009. BLAST+: architecture and applications. BMC Bioinformatics, 10, 421.*

Museoscript recoded following original concept Linux bash script:

> *Rancilhac, L., Bruy, T., Scherz, M. D., Pereira, E. A., Preick, M., Straube, N., Lyra, M. L., Ohler, A., Streicher, J. W., Andreone,
    F., Crottini, A., Hutter, C. R., Randrianantoandro,J. C., Rokotoarison, A., Glaw, F., Hofreiter, M. & Vences, M. (2020).
    Target-enriched DNA sequencing from historical type material enables a partial revision of the Madagascar giant stream frogs (genus Mantidactylus).
    Journal of Natural History, 1-32.*
