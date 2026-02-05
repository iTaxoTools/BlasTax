import re
import unicodedata
from pathlib import Path


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


class FastqParseError(Exception):
    def __init__(self, path: Path | str):
        self.path = Path(path)
        super().__init__(f"Could not parse fastq file: {path.name}")


def fastq_to_fasta(fastq_path: Path | str, fasta_file: Path | str):
    """Quick conversion from FastQ to FASTA"""
    with open(fastq_path, "r") as fastq_file:
        with open(fasta_file, "w") as fasta_file:
            id = None
            seq = None
            for line in fastq_file:
                if not line.strip():
                    continue
                if line.startswith("@"):
                    id = line.removeprefix("@").strip()
                    continue
                if id is not None and seq is None:
                    seq = line.strip()
                    continue
                if line.startswith("+"):
                    if id is None or seq is None:
                        raise FastqParseError(fastq_path)
                    fastq_file.readline()
                    print(f">{id}", end="\n", file=fasta_file)
                    print(seq, end="\n", file=fasta_file)
                    id = None
                    seq = None
                    continue


def is_fasta(path: Path | str) -> bool:
    with open(path, "r") as file:
        for line in file:
            if not line.strip():
                continue
            if line.startswith(";"):
                continue
            if line.startswith(">"):
                return True
    return False


def is_fastq(path: Path | str) -> bool:
    with open(path, "r") as file:
        id = False
        for line in file:
            if not line.strip():
                continue
            if line.startswith("@"):
                id = True
            if line.startswith("+"):
                return bool(id)
    return False


# Utils for fasta name modifier
def string_trimmer(
    komm_zeile: str,
    counter: int,
    trim: bool,
    add: bool,
    replace: bool,
    sanitize: bool,
    trimpos: str,
    trimmaxchar: int,
    auto: bool,
    letters_and_numbers: str,
    direc: str = None,
    addstring: str = None,
    findstring: str = None,
    replacestring: str = None,
) -> str:
    # The dictionary used to translate extended ASCII into ASCII representation by lib.utils.sanitize
    ext_ascii_trans = {
        "ƒ": "f",
        "Š": "S",
        "Œ": "OE",
        "Ž": "Z",
        "š": "s",
        "œ": "oe",
        "ž": "z",
        "Ÿ": "Y",
        "¡": "i",
        "¢": "c",
        "ª": "a",
        "²": "2",
        "³": "3",
        "µ": "u",
        "¹": "1",
        "º": "o",
        "À": "A",
        "Á": "A",
        "Â": "A",
        "Ã": "A",
        "Ä": "Ae",
        "Å": "A",
        "Æ": "Ae",
        "Ç": "C",
        "È": "E",
        "É": "E",
        "Ê": "E",
        "Ë": "E",
        "Ì": "I",
        "Í": "I",
        "Î": "I",
        "Ï": "I",
        "Ð": "D",
        "Ñ": "N",
        "Ò": "O",
        "Ó": "O",
        "Ô": "O",
        "Õ": "O",
        "Ö": "Oe",
        "×": "x",
        "Ø": "O",
        "Ù": "U",
        "Ú": "U",
        "Û": "U",
        "Ü": "Ue",
        "Ý": "Y",
        "ß": "ss",
        "à": "a",
        "á": "a",
        "â": "a",
        "ã": "a",
        "ä": "ae",
        "å": "a",
        "æ": "a",
        "ç": "c",
        "è": "e",
        "é": "e",
        "ê": "e",
        "ë": "e",
        "ì": "i",
        "í": "i",
        "î": "i",
        "ï": "i",
        "ð": "d",
        "ñ": "n",
        "ò": "o",
        "ó": "o",
        "ô": "o",
        "õ": "o",
        "ö": "oe",
        "ù": "ue",
        "ú": "ue",
        "û": "ue",
        "ü": "ue",
        "ý": "y",
        "ÿ": "y",
    }
    komm_zeile = unicodedata.normalize("NFC", komm_zeile)
    new_komm = komm_zeile
    laenge = len(new_komm)
    nk = ""

    new_komm = komm_zeile.replace("﻿>", ">")  # Replace look-alike characters

    # Adding string at the beginning or end
    if add:
        if direc == "beginning":
            strippi = new_komm.lstrip(">")
            new_komm = ">" + addstring + strippi
        elif direc == "end":
            new_komm = new_komm + addstring

    # Replacing strings
    if replace:
        new_komm = ">" + new_komm[1:].replace(findstring, replacestring)

    # Trimming
    if trim:
        counterpad = len(str(int(counter))) - 1
        if auto:
            trimmaxchar = int(trimmaxchar) - counterpad - 1
        else:
            trimmaxchar = int(trimmaxchar) - counterpad

        if trimpos == "beginning":
            startpos = laenge - int(trimmaxchar)
            new_komm = ">" + new_komm[startpos:]
        elif trimpos == "end":
            endpos = int(trimmaxchar)
            new_komm = ">" + new_komm[1:endpos]

    # Autoincrement
    if auto:
        new_komm = f"{new_komm}_{counter}"
    # Sanitization: Replace characters not in letters_and_numbers with '_'
    if sanitize:
        nk = ""
        for zeichen in new_komm:
            if zeichen in letters_and_numbers:
                nk += zeichen
            else:
                translated_char = ext_ascii_trans.get(zeichen)
                if translated_char:
                    nk += translated_char
                else:
                    nk += "_"
        new_komm = nk

    return new_komm


def make_str_blast_safe(text: str) -> str:
    return text.encode("ascii", "replace").decode().translate(str.maketrans("? ", "__"))
