# Translator, AKS, 02.09.24, Anpassungen ab 28.10.24, Korrekturen 08.04.25

import sys
from dataclasses import dataclass, field
from functools import partial
from os import devnull
from pathlib import Path
from typing import Literal, TextIO

from Bio import SeqIO
from Bio.SeqRecord import SeqRecord

# print(Bio.Data.CodonTable.standard_dna_table)
STOPS = ["TAA", "TAG", "TGA"]


@dataclass
class Options:
    input_path: Path
    output_path: Path | None
    log_path: Path | None
    nucleotide_path: Path | None

    input_type: Literal["cds", "cds_stop", "transcript ", "all"]
    frame: Literal["autodetect", "1", "2", "3", "4", "5", "6"]
    code: str | int  # codon table

    stop: Literal["yes", "no"] = field(init=False, default=None)
    input_file: TextIO = field(init=False, default=None)
    output_file: TextIO = field(init=False, default=None)
    log_file: TextIO = field(init=False, default=None)
    nucleotide_file: TextIO = field(init=False, default=None)
    translation_6: TextIO = field(init=False, default=None)

    def __post_init__(self):
        if self.output_path is None:
            self.output_path = self.input_path.with_stem(self.input_path.stem + "_aa")
            self.output_path = self.output_path.with_suffix(".fasta")
        if self.log_path is None:
            self.log_path = Path(devnull)
        if self.nucleotide_path is None:
            self.nucleotide_path = Path(devnull)
        if self.input_type == "cds":
            self.stop = "no"
        elif self.input_type == "cds_stop":
            self.stop = "no"
        else:
            self.stop = "yes"
        self.input_file = open(self.input_path, "r")
        self.output_file = open(self.output_path, "w")
        self.log_file = open(self.log_path, "w")
        self.nucleotide_file = open(self.nucleotide_path, "w")
        if self.input_type == "all":
            self.translation_6 = self.output_path.with_name("translation_6.fasta")

    def close_files(self):
        self.input_file.close()
        self.output_file.close()
        self.log_file.close()
        self.nucleotide_file.close()


def prot_record(record, options: Options):
    protein = translate_DNA_record(record, options)
    return SeqRecord(seq=protein, id=record.id + "_translated_sequence", description="")


# special function for mode all
def prot_record_solo(record, options: Options):
    alloutput = options.output_file
    proteinall = ""
    for zae in range(1, 7):
        protein = translate_DNA_record_solo(record, options.code, zae)
        proteinall = proteinall + protein + "\n"
    # records = SeqRecord(seq=protein, id=">" + record.id, description="_translated_sequence")
    alloutput.write(">" + record.id + "\n")
    alloutput.write(str(proteinall))
    return SeqRecord(seq=protein, id=record.id + "_translated_sequence", description="")


def translate_DNA_record(record, options: Options):
    table_nr = options.code
    input_type = options.input_type
    frame = options.frame
    stop = options.stop
    loggi = options.log_file
    nucli = options.nucleotide_file

    if len(record) % 3 == 0:
        orf1 = record.seq.translate(table=table_nr)
        orf2 = record.seq[1:-3].translate(table=table_nr)
        orf3 = record.seq[2:-2].translate(table=table_nr)

        orf1rc = record.seq.reverse_complement().translate(table=table_nr)
        orf2rc = record.seq[1:-3].reverse_complement().translate(table=table_nr)
        orf3rc = record.seq[2:-2].reverse_complement().translate(table=table_nr)

    elif len(record) % 3 == 1:
        orf1 = record.seq[0:-2].translate(table=table_nr)
        orf2 = record.seq[1:-1].translate(table=table_nr)
        orf3 = record.seq[2:-3].translate(table=table_nr)

        orf1rc = record.seq[0:-2].reverse_complement().translate(table=table_nr)
        orf2rc = record.seq[1:-1].reverse_complement().translate(table=table_nr)
        orf3rc = record.seq[2:-3].reverse_complement().translate(table=table_nr)

    elif len(record) % 3 == 2:
        orf1 = record.seq[0:-3].translate(table=table_nr)
        orf2 = record.seq[1:-2].translate(table=table_nr)
        orf3 = record.seq[2:-1].translate(table=table_nr)

        orf1rc = record.seq[0:-3].reverse_complement().translate(table=table_nr)
        orf2rc = record.seq[1:-2].reverse_complement().translate(table=table_nr)
        orf3rc = record.seq[2:-1].reverse_complement().translate(table=table_nr)

    orf_dict = {"orf1": orf1, "orf2": orf2, "orf3": orf3, "orf1rc": orf1rc, "orf2rc": orf2rc, "orf3rc": orf3rc}
    orf_list = []
    for elem in orf_dict:
        orf_list.append(orf_dict[elem])
    orf_wanted = orf1
    orf_label = "orf1"
    if input_type == "cds":
        if frame == "1":
            orf_wanted = orf1
            orf_label = "orf1"
        elif frame == "2":
            orf_wanted = orf2
            orf_label = "orf2"
        elif frame == "3":
            orf_wanted = orf3
            orf_label = "orf3"
        elif frame == "4":
            orf_wanted = orf1rc
            orf_label = "orf1rc"
        elif frame == "5":
            orf_wanted = orf2rc
            orf_label = "orf2rc"
        elif frame == "6":
            orf_wanted = orf3rc
            orf_label = "orf3rc"
        elif frame == "autodetect":
            if stop == "no":
                count_stopless = 0
                another = 0
                if "*" not in orf1:
                    orf_wanted = orf1
                    orf_label = "orf1"
                    count_stopless = count_stopless + 1
                # loggi.write(str(orf_wanted)+'\n')
                if "*" not in orf2:
                    orf_wanted = orf2
                    orf_label = "orf2"
                    count_stopless = count_stopless + 1
                    if count_stopless > 1:
                        loggi.write("\n" + record.id + "\n")
                        loggi.write(
                            "Warning: For this sequence more than one translation without stops was found:" + "\n"
                        )
                        another = 1
                        loggi.write(orf_label + ": " + str(orf_wanted) + "\n")
                if "*" not in orf3:
                    orf_wanted = orf3
                    orf_label = "orf3"
                    count_stopless = count_stopless + 1
                    if count_stopless > 1:
                        if not another:
                            loggi.write("\n" + record.id + "\n")
                            loggi.write(
                                "Warning: For this sequence more than one translation without stops was found:" + "\n"
                            )
                            another = 1
                        loggi.write(orf_label + ": " + str(orf_wanted) + "\n")
                if "*" not in orf1rc:
                    orf_wanted = orf1rc
                    orf_label = "orf1rc"
                    count_stopless = count_stopless + 1
                    if count_stopless > 1:
                        if not another:
                            loggi.write("\n" + record.id + "\n")
                            loggi.write(
                                "Warning: For this sequence more than one translation without stops was found:" + "\n"
                            )
                            another = 1
                        loggi.write(orf_label + ": " + str(orf_wanted) + "\n")
                if "*" not in orf2rc:
                    orf_wanted = orf2rc
                    orf_label = "orf2rc"
                    count_stopless = count_stopless + 1
                    if count_stopless > 1:
                        if not another:
                            loggi.write("\n" + record.id + "\n")
                            loggi.write(
                                "Warning: For this sequence more than one translation without stops was found:" + "\n"
                            )
                            another = 1
                        loggi.write(orf_label + ": " + str(orf_wanted) + "\n")
                if "*" not in orf3rc:
                    orf_wanted = orf3rc
                    orf_label = "orf3rc"
                    if count_stopless > 1:
                        if not another:
                            loggi.write("\n" + record.id + "\n")
                            loggi.write(
                                "Warning: For this sequence more than one translation without stops was found:" + "\n"
                            )
                            another = 1
                        loggi.write(orf_label + ": " + str(orf_wanted) + "\n")
                # loggi.write('\n')
                # no translation without stops
                if count_stopless == 0:
                    nr_stops_list = []
                    for orf in orf_list:
                        nr_stops = str(orf).count("*")
                        if orf[-1] == "*":
                            nr_stops = 999
                        nr_stops_list.append(nr_stops)
                    min_stops = min(nr_stops_list)
                    pos = nr_stops_list.index(min_stops)
                    doppelt = 0
                    for i in range(0, len(nr_stops_list)):
                        testnr = nr_stops_list[i]
                        for j in range(0, len(nr_stops_list) - (i + 1)):
                            if testnr == nr_stops_list[i]:
                                doppelt = testnr
                                # doppel_pos = nr_stops_list.index(doppelt)

                    orf_wanted = orf_list[pos]
                    loggi.write("\n" + record.id + "\n")
                    loggi.write("Warning: For this sequence no translation without stops was found." + "\n")
                    loggi.write("Translation with minimal number of stops is:" + "\n")
                    # loggi.write(str(nr_stops_list)+'\n')
                    # loggi.write(str(min_stops)+'\n')
                    # loggi.write('doppelt ist'+str(doppelt)+str(doppel_pos)+'\n')
                    loggi.write(str(orf_wanted) + "\n" + "\n")
                    if doppelt == min_stops:
                        loggi.write("There are two translations with minimal number of stops " + "\n")

    if input_type == "cds_stop":
        if frame == "1":
            orf_wanted = orf1
            orf_label = "orf1"
        elif frame == "2":
            orf_wanted = orf2
            orf_label = "orf2"
        elif frame == "3":
            orf_wanted = orf3
            orf_label = "orf3"
        elif frame == "4":
            orf_wanted = orf1rc
            orf_label = "orf1rc"
        elif frame == "5":
            orf_wanted = orf2rc
            orf_label = "orf2rc"
        elif frame == "6":
            orf_wanted = orf3rc
            orf_label = "orf3rc"
        elif frame == "autodetect":
            if stop == "no":
                if "*" not in orf1:
                    orf_wanted = orf1
                    orf_label = "orf1"
                elif "*" not in orf2:
                    orf_wanted = orf2
                    orf_label = "orf2"
                elif "*" not in orf3:
                    orf_wanted = orf3
                    orf_label = "orf3"
                elif "*" not in orf1rc:
                    orf_wanted = orf1rc
                    orf_label = "orf1rc"
                elif "*" not in orf2rc:
                    orf_wanted = orf2rc
                    orf_label = "orf2rc"
                elif "*" not in orf3rc:
                    orf_wanted = orf3rc
                    orf_label = "orf3rc"
                # no translation without stops
                else:
                    nr_stops_list = []
                    for orf in orf_list:
                        nr_stops = str(orf).count("*")
                        nr_stops_list.append(nr_stops)
                    min_stops = min(nr_stops_list)
                    pos = nr_stops_list.index(min_stops)
                    orf_wanted = orf_list[pos]

    if input_type == "transcript":
        orf_label = "none"
        if "*" not in orf1:
            orf_wanted = orf1
            orf_label = "orf1"
        if "*" not in orf2:
            orf_wanted = orf2
            orf_label = "orf2"
        if "*" not in orf3:
            orf_wanted = orf3
            orf_label = "orf3"
        if "*" not in orf1rc:
            orf_wanted = orf1rc
            orf_label = "orf1rc"
        if "*" not in orf2rc:
            orf_wanted = orf2rc
            orf_label = "orf2rc"
        if "*" not in orf3rc:
            orf_wanted = orf3rc
            orf_label = "orf3rc"
        loggi.write(record.id + "\n")
        # no sequence without stops
        if orf_label == "none":
            wanted_len = 0
            zae = 0
            for orf in orf_list:
                nr_stops = str(orf).count("*")
                splitti = orf.split("*")
                i = 0
                maxi = 0
                index = 0

                loggi.write(str(orf) + "\n" + str(nr_stops) + "\n")
                for sp in splitti:
                    loggi.write(str(sp) + " " + str(len(sp)) + "\n")
                    if len(sp) > maxi:
                        index = i
                        maxi = len(sp)
                    i = i + 1
                loggi.write("max ist " + str(splitti[index]) + " " + str(len(splitti[index])) + "\n")
                loggi.write("\n")
                if len(splitti[index]) > wanted_len:
                    orf_wanted = splitti[index]
                    pos_orf = str(orf).find(str(orf_wanted))
                    wanted_len = len(splitti[index])
                    orf_key = list(orf_dict.keys())
                    orf_label = orf_key[zae]
                zae = zae + 1
            loggi.write(
                "orf_wanted is "
                + str(orf_wanted)
                + " "
                + str(len(str(orf_wanted)))
                + " "
                + str(pos_orf)
                + " "
                + orf_label
                + "\n"
            )
            full_orf_len = len(str(orf_dict[orf_label]))
            if orf_label == "orf1":
                dna_start = pos_orf * 3
                dna_end = dna_start + wanted_len * 3
            elif orf_label == "orf2":
                dna_start = (pos_orf * 3) + 1
                dna_end = dna_start + (wanted_len * 3) - 2
            elif orf_label == "orf3":
                dna_start = (pos_orf * 3) + 2
                dna_end = dna_start + (wanted_len * 3) + 2
            elif orf_label == "orf1rc":
                dna_start = full_orf_len * 3 - ((wanted_len + 1) * 3)
                dna_end = dna_start + wanted_len * 3
            elif orf_label == "orf2rc":
                dna_start = (pos_orf * 3) + 2
                dna_end = dna_start + (wanted_len * 3) + 2
            elif orf_label == "orf3rc":
                dna_start = (pos_orf * 3) + 2
                dna_end = dna_start + (wanted_len * 3) + 2
            else:
                raise Exception("Unexpected ORF label: " + orf_label)
            orfx = record.seq[dna_start:dna_end].translate(table=table_nr)

            loggi.write(
                "dna "
                + str(record.seq[dna_start + 1 : dna_end + 1])
                + str(dna_start + 1)
                + " "
                + str(dna_end + 1)
                + str(orfx)
                + "\n"
            )
            nucli.write(">" + record.id + "\n")
            nucli.write(str(record.seq[dna_start:dna_end]) + "\n")

        else:
            nucli.write(">" + record.id + "\n")
            pos_orf = 0
            wanted_len = len(orf_wanted)
            if orf_label == "orf1":
                dna_start = pos_orf * 3
                dna_end = dna_start + wanted_len * 3
            elif orf_label == "orf2":
                dna_start = (pos_orf * 3) + 1
                dna_end = dna_start + (wanted_len * 3) - 2
            elif orf_label == "orf3":
                dna_start = (pos_orf * 3) + 2
                dna_end = dna_start + (wanted_len * 3) + 2
            elif orf_label == "orf1rc":
                dna_start = full_orf_len * 3 - ((wanted_len + 1) * 3)
                dna_end = dna_start + wanted_len * 3
            elif orf_label == "orf2rc":
                dna_start = (pos_orf * 3) + 2
                dna_end = dna_start + (wanted_len * 3) + 2
            elif orf_label == "orf3rc":
                dna_start = (pos_orf * 3) + 2
                dna_end = dna_start + (wanted_len * 3) + 2
            else:
                raise Exception("Unexpected ORF label: " + orf_label)
            orfx = record.seq[dna_start:dna_end].translate(table=table_nr)

            loggi.write(
                "dna "
                + str(record.seq[dna_start + 1 : dna_end + 1])
                + str(dna_start + 1)
                + " "
                + str(dna_end + 1)
                + str(orfx)
                + "\n"
            )
            nucli.write(str(record.seq[dna_start:dna_end]) + "\n")

    return orf_wanted


# special function for mode all
def translate_DNA_record_solo(record, table_nr, nr):
    if len(record) % 3 == 0:
        orf1 = record.seq.translate(table=table_nr)
        orf2 = record.seq[1:-3].translate(table=table_nr)
        orf3 = record.seq[2:-2].translate(table=table_nr)

        orf1rc = record.seq.reverse_complement().translate(table=table_nr)
        orf2rc = record.seq[1:-3].reverse_complement().translate(table=table_nr)
        orf3rc = record.seq[2:-2].reverse_complement().translate(table=table_nr)

    elif len(record) % 3 == 1:
        orf1 = record.seq[0:-2].translate(table=table_nr)
        orf2 = record.seq[1:-1].translate(table=table_nr)
        orf3 = record.seq[2:-3].translate(table=table_nr)

        orf1rc = record.seq[0:-2].reverse_complement().translate(table=table_nr)
        orf2rc = record.seq[1:-1].reverse_complement().translate(table=table_nr)
        orf3rc = record.seq[2:-3].reverse_complement().translate(table=table_nr)

    elif len(record) % 3 == 2:
        orf1 = record.seq[0:-3].translate(table=table_nr)
        orf2 = record.seq[1:-2].translate(table=table_nr)
        orf3 = record.seq[2:-1].translate(table=table_nr)

        orf1rc = record.seq[0:-3].reverse_complement().translate(table=table_nr)
        orf2rc = record.seq[1:-2].reverse_complement().translate(table=table_nr)
        orf3rc = record.seq[2:-1].reverse_complement().translate(table=table_nr)

    if nr == 1:
        orf_wanted = orf1
        # orf_label = "orf1"
    elif nr == 2:
        orf_wanted = orf2
        # orf_label = "orf2"
    elif nr == 3:
        orf_wanted = orf3
        # orf_label = "orf3"
    elif nr == 4:
        orf_wanted = orf1rc
        # orf_label = "orf1rc"
    elif nr == 5:
        orf_wanted = orf2rc
        # orf_label = "orf2rc"
    elif nr == 6:
        orf_wanted = orf3rc
        # orf_label = "orf3rc"

    return orf_wanted


def translate(options: Options):
    if options.input_type == "all":
        prot_record_solo_partial = partial(prot_record_solo, options=options)
        records = map(prot_record_solo_partial, SeqIO.parse(options.input_file, "fasta"))
        SeqIO.write(records, options.translation_6, "fasta")
    else:
        prot_record_partial = partial(prot_record, options=options)
        records = map(prot_record_partial, SeqIO.parse(options.input_file, "fasta"))
        options.output_file.close()
        SeqIO.write(records, options.output_path, "fasta")
    options.close_files()


if __name__ == "__main__":
    options = Options(
        input_path=Path(sys.argv[2]),
        output_path=Path(sys.argv[14]) if len(sys.argv) > 14 else None,
        log_path=Path("translator.log"),
        nucleotide_path=Path("nucleotids"),
        input_type=sys.argv[4],
        frame=sys.argv[8],
        code=sys.argv[10],
    )
    translate(options)
