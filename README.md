# BlasTax

[![PyPI - Version](https://img.shields.io/pypi/v/itaxotools-blastax?color=tomato)](
    https://pypi.org/project/itaxotools-blastax)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/itaxotools-blastax)](
    https://pypi.org/project/itaxotools-blastax)
[![GitHub - Tests](https://img.shields.io/github/actions/workflow/status/iTaxoTools/BlasTax/test.yml?label=tests)](
    https://github.com/iTaxoTools/BlasTax/actions/workflows/test.yml)
[![GitHub - Windows](https://img.shields.io/github/actions/workflow/status/iTaxoTools/BlasTax/windows.yml?label=windows)](
    https://github.com/iTaxoTools/BlasTax/actions/workflows/windows.yml)
[![GitHub - macOS](https://img.shields.io/github/actions/workflow/status/iTaxoTools/BlasTax/macos.yml?label=macos)](
    https://github.com/iTaxoTools/BlasTax/actions/workflows/macos.yml)

A graphical user interface to run BLAST and parse hits:

- **Make BLAST database**: Create a BLAST database from a sequence file
- **Regular BLAST**: Find regions of similarity between sequences in a query file and a BLAST database
- **BLAST-Append**: Append the aligned part of matching sequences to the original query sequences
- **BLAST-Append-X**: Like BLAST-Append, but appends nucleotides c orresponding to the protein database
- **Decontaminate**: Remove contaminants from query sequences based on two ingroup and outgroup databases
- **Museoscript**: Create sequence files from BLAST matches

The program also includes a variety of tools for processing FASTA files:

- **Fast prepare**: Rename FASTA sequence identifiers in preparation for BLAST analysis
- **Fast split**: Split large sequences or text files into smaller files
- **Fast merge**: Merge multiple sequences or text files into a single large file
- **Group merge**: Merge FASTA files by filename
- **Removal of stop codons**: Remove stop codons from a dataset
- **Codon trimming**: Trim coding sequences to start with first codon position

Some extra tools are also available:

- **SCaFoSpy**: Create chimerical sequences for species
- **Protein translator**: Generate protein translations for each sequence
- **MAFFT alignment**: Multiple sequence alignment using MAFFTpy
- **Codon-aware alignment**: Align nucleotide sequences as proteins without altering codons
- **Cutadapt**: Remove adapter sequences and quality trimming

Input sequences must be in the FASTA or FASTQ file formats.

![Screenshot](https://raw.githubusercontent.com/iTaxoTools/BlasTax/main/images/screenshot.png)

## Executables

Download and run the standalone executables without installing Python or BLAST+.

[![Release](https://img.shields.io/badge/release-BlasTax_0.1.1-red?style=for-the-badge)](
    https://github.com/iTaxoTools/BlasTax/releases/v0.1.1)
[![Windows](https://img.shields.io/badge/Windows-blue.svg?style=for-the-badge&logo=data:image/svg+xml;base64,PD94bWwgdmVyc2lvbj0iMS4wIiBlbmNvZGluZz0iVVRGLTgiPz4KPCEtLSBDcmVhdGVkIHdpdGggSW5rc2NhcGUgKGh0dHA6Ly93d3cuaW5rc2NhcGUub3JnLykgLS0+Cjxzdmcgd2lkdGg9IjQ4IiBoZWlnaHQ9IjQ4IiB2ZXJzaW9uPSIxLjEiIHZpZXdCb3g9IjAgMCAxMi43IDEyLjciIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CiA8ZyBmaWxsPSIjZmZmIiBzdHJva2UtbGluZWNhcD0ic3F1YXJlIiBzdHJva2Utd2lkdGg9IjMuMTc0OSI+CiAgPHJlY3QgeD0iLjc5MzczIiB5PSIuNzkzNzMiIHdpZHRoPSI1LjAyNyIgaGVpZ2h0PSI1LjAyNyIvPgogIDxyZWN0IHg9IjcuMTQzNiIgeT0iLjc5MzczIiB3aWR0aD0iNC43NjI0IiBoZWlnaHQ9IjUuMDI3Ii8+CiAgPHJlY3QgeD0iLjc5MzczIiB5PSI2Ljg3OSIgd2lkdGg9IjUuMDI3IiBoZWlnaHQ9IjUuMDI3Ii8+CiAgPHJlY3QgeD0iNy4xNDM2IiB5PSI2Ljg3OSIgd2lkdGg9IjQuNzYyNCIgaGVpZ2h0PSI1LjAyNyIvPgogPC9nPgo8L3N2Zz4K)](
    https://github.com/iTaxoTools/BlasTax/releases/download/v0.1.1/BlasTax-0.1.1-windows-x64.exe)
[![MacOS](https://img.shields.io/badge/macOS-slategray.svg?style=for-the-badge&logo=apple)](
    https://github.com/iTaxoTools/BlasTax/releases/download/v0.1.1/BlasTax-0.1.1-macos-universal2.dmg)

## Installation

BlasTax is available on PyPI and can be installed using `pip`:

```
pip install itaxotools-blastax
```

After installation, run the program with:

```
blastax
```

If the BLAST+ binaries are not found in your system PATH at runtime, the program will prompt you to
automatically download them to your system-specific configuration directory (under iTaxoTools/BlasTax, see [platformdirs](https://pypi.org/project/platformdirs/)).

To reset the location where the program looks for BLAST+, run:

```
blastax --reset
```

## Citations

*BlasTax* was developed in the framework of the *iTaxoTools* project:

> *Vences M. et al. (2021): iTaxoTools 0.1: Kickstarting a specimen-based software toolkit for taxonomists. - Megataxa 6: 77-92.*

Code by Nikita Kulikov, Anja-Kristina Schulz and Stefanos Patmanidis.

---

BlasTax integrates the BLAST+ suite from NCBI:

> *Camacho, C., Coulouris, G., Avagyan, V., Ma, N., Papadopoulos, J., Bealer, K., and Madden, T.L. 2009. BLAST+: architecture and applications. BMC Bioinformatics, 10, 421.*

Cutadapt is included as a Python module to remove adapter sequences from high-throughput sequencing reads:

> *Martin, M. (2011). Cutadapt removes adapter sequences from high-throughput sequencing reads. EMBnet.journal, 17(1), 10-12.*

Museoscript was rewritten following the original concept of the Linux bash script:

> *Rancilhac, L., Bruy, T., Scherz, M. D., Pereira, E. A., Preick, M., Straube, N., Lyra, M. L., Ohler, A., Streicher, J. W., Andreone,
    F., Crottini, A., Hutter, C. R., Randrianantoandro,J. C., Rokotoarison, A., Glaw, F., Hofreiter, M. & Vences, M. (2020).
    Target-enriched DNA sequencing from historical type material enables a partial revision of the Madagascar giant stream frogs (genus Mantidactylus).
    Journal of Natural History, 1-32.*

MAFFT is a multiple sequence alignment program that was integrated using MAFFTpy:

> *Katoh, K., Misawa, K., Kuma, K., & Miyata, T. (2002). MAFFT: a novel method for rapid multiple sequence alignment based on fast Fourier transform. Nucleic Acids Research, 30(14), 3059-3066.*
