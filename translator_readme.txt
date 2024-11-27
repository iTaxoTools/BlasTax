Script uses FASTA-File with nucleotid sequences as input
Biophython is needed

Generates translation of each sequence in the input file using different modi (input_type paramter):

    -all
    All six possible translations

    -transscript
    Searching for the longest open reading frame (the longest sequence part without stops), writing orf into FASTA-File
    Additionally writes nucleotide sequences of the ORF in separate file

    -cds
    Searching for the translation without any stop or minimal number of stops

    -cds_stop
    searching for the translation without any stop or minimal number of stops; terminal stops preferred

Parameters are:
    name of the FASTA Input File (-input_name)
    name of the FASTA Output File (-output_name), if missing: output_name=input_name+'_aa'+'.fasta'
    26 translation tables possible (-code)
    frame for translation (-frame), autodetect is default

The script also generates a log file with some special informations(translator.log)


----

Example script call:
```
python .\translator.py i data/mala.fas type all stop yes frame 1 code 1 log yes out foobar.buz
```

ORF = open reading frame

input type in [all, cds, cds_stop, transcript]

-input_type
Options: cds, cds_stop, transcript, all
default: cds (stands for coding sequence), so -input_type cds
With the input_type all, all 6 frames are translated and all included in the output fasta.
The "stopcodon" option is omitted and is included in the input type "cds_stop".

-frame
Options: 1, 2, 3, 4, 5, 6, autodetect
default: autodetect

- code
Options: 1, 2, 3, 4, 5, .... 26, autodetect
default: 1 (so the standard code, I assume that this is 1).

-output_type
Options: fasta, fasta_log
Either only the fasta file is output or an additional log file.
Default: fasta

-out
Options: Here the user can enter the name of the out file. This name would be used for both the fasta and log file (each with different extensions).
Default: If nothing is entered, the name of the input file with the addition _aa is used.