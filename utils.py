import re


def check_fasta_headers(file_path):
    """Check if any header in the FASTA file is longer than 51 characters or contains special characters, allowing underscores and '>'."""
    # Define invalid characters as a regex pattern (excluding underscores and '>')
    invalid_chars_pattern = re.compile(r"[^\w\s>]")

    with open(file_path, "r") as file:
        for line in file:
            if line.startswith(">"):  # Header line starts with '>'
                header = line.strip()
                if len(header) > 51:
                    return "length"
                if invalid_chars_pattern.search(header):
                    return "special"


def remove_gaps(input_path, output_path):
    """Remove all gaps from the input files"""
    with open(input_path, "r") as infile, open(output_path, "w") as outfile:
        for line in infile:
            if not line.startswith(">"):
                modified_line = line.replace("-", "")
                outfile.write(modified_line)
            else:
                outfile.write(line)


### LOOP-BLASTX FILE POSTPROCESSING ###
# FUNKTIONEN TRANSLATE
# Triplett Zuordnung AS
def trans_triplett(triplett):
    # Dictionary mapping triplet codes to amino acids
    codon_map = {
        "TTT": "F",
        "TTC": "F",
        "TTA": "L",
        "TTG": "L",
        "TCT": "S",
        "TCC": "S",
        "TCA": "S",
        "TCG": "S",
        "TAT": "Y",
        "TAC": "Y",
        "TAA": "X",
        "TAG": "X",
        "TGT": "C",
        "TGC": "C",
        "TGA": "X",
        "TGG": "W",
        "CTT": "L",
        "CTC": "L",
        "CTA": "L",
        "CTG": "L",
        "CCT": "P",
        "CCC": "P",
        "CCA": "P",
        "CCG": "P",
        "CAT": "H",
        "CAC": "H",
        "CAA": "Q",
        "CAG": "Q",
        "CGT": "R",
        "CGC": "R",
        "CGA": "R",
        "CGG": "R",
        "ATT": "I",
        "ATC": "I",
        "ATA": "I",
        "ATG": "M",
        "ACT": "T",
        "ACC": "T",
        "ACA": "T",
        "ACG": "T",
        "AAT": "N",
        "AAC": "N",
        "AAA": "K",
        "AAG": "K",
        "AGT": "S",
        "AGC": "S",
        "AGA": "R",
        "AGG": "R",
        "GTT": "V",
        "GTC": "V",
        "GTA": "V",
        "GTG": "V",
        "GCT": "A",
        "GCC": "A",
        "GCA": "A",
        "GCG": "A",
        "GAT": "D",
        "GAC": "D",
        "GAA": "E",
        "GAG": "E",
        "GGT": "G",
        "GGC": "G",
        "GGA": "G",
        "GGG": "G",
    }
    return codon_map.get(triplett, "X")


def complement(seq):
    comp = ""
    for i in range(0, len(seq)):
        if seq[i] == "A":
            comp = comp + "T"
        elif seq[i] == "T":
            comp = comp + "A"
        elif seq[i] == "G":
            comp = comp + "C"
        elif seq[i] == "C":
            comp = comp + "G"
    return comp


def translate(line):
    prot_list = []
    ami_string_frame1 = ""
    for i in range(0, len(line) - 1, 3):
        ami = trans_triplett(line[i : i + 3])
        ami_string_frame1 = ami_string_frame1 + ami
    prot_list.append(ami_string_frame1)
    ami_string_frame2 = ""
    for i in range(1, len(line) - 3, 3):
        ami = trans_triplett(line[i : i + 3])
        ami_string_frame2 = ami_string_frame2 + ami
    prot_list.append(ami_string_frame2)
    ami_string_frame3 = ""
    for i in range(2, len(line) - 3, 3):
        ami = trans_triplett(line[i : i + 3])
        ami_string_frame3 = ami_string_frame3 + ami
    prot_list.append(ami_string_frame3)
    compi = complement(line)
    reverse = compi[::-1]
    ami_string_frame1r = ""
    for i in range(0, len(reverse) - 1, 3):
        ami = trans_triplett(reverse[i : i + 3])
        ami_string_frame1r = ami_string_frame1r + ami
    prot_list.append(ami_string_frame1r)
    ami_string_frame2r = ""
    for i in range(1, len(reverse) - 3, 3):
        ami = trans_triplett(reverse[i : i + 3])
        ami_string_frame2r = ami_string_frame2r + ami
    prot_list.append(ami_string_frame2r)
    ami_string_frame3r = ""
    for i in range(2, len(reverse) - 3, 3):
        ami = trans_triplett(reverse[i : i + 3])
        ami_string_frame3r = ami_string_frame3r + ami
    prot_list.append(ami_string_frame3r)
    return prot_list


# ENDE TRANSLATE

def fastq_to_fasta(infile, outfile) -> None:
    """Quick conversion from FastQ to FASTA"""
    fastq_file = open(infile, 'r')
    fasta_file = open(outfile, 'w')

    for line in fastq_file:
        # loop through lines until the start of a record
        if line[0] == "@":
            # copy the seqid
            print(">", line[1:], sep="", end="", file=fasta_file)
            # copy the sequence
            line = fastq_file.readline()
            print(line, file=fasta_file, end="")
    fastq_file.close()
    fasta_file.close()