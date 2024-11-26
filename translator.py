# Translator, AKS, 02.09.24, Anpassungen ab 28.10.24

import sys

from Bio import SeqIO
from Bio.SeqRecord import SeqRecord

# print(Bio.Data.CodonTable.standard_dna_table)
stops = ["TAA", "TAG", "TGA"]

arg_len = len(sys.argv)
input_name = sys.argv[2]
input_type = sys.argv[4]
stop = sys.argv[6]
frame = sys.argv[8]
code = sys.argv[10]
output_type = sys.argv[12]
if arg_len > 14:
    output_name = sys.argv[14]
if arg_len <= 14:
    out_split = input_name.split(".")
    output_name = out_split[0] + "_aa" + ".fasta"
log_file = "translator.log"
nucl_file = "nucleotids"
loggi = open(log_file, "w")
nucli = open(nucl_file, "w")

global_yes_fasta = 1

# overwriting parameter argv6
if input_type == "cds":
    stop = "no"
if input_type == "cds_stop":
    stop = "no"


def prot_record(record):
    protein = translate_DNA_record(record, code)
    return SeqRecord(seq=protein, id=">" + record.id, description="translated sequenz")


# special function for mode all
def prot_record_solo(record):
    proteinall = ""
    for zae in range(1, 7):
        protein = translate_DNA_record_solo(record, code, zae)
        proteinall = proteinall + protein + "\n"
    # records = SeqRecord(seq=protein, id=">" + record.id, description="translated sequenz")
    alloutput.write(">" + record.id + "\n")
    alloutput.write(str(proteinall))
    return SeqRecord(seq=protein, id=">" + record.id, description="translated sequenz")


def translate_DNA_record(record, table_nr):
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

    orf_dict = {"orf1": orf1, "orf2": orf2, "orf3": orf3, "orf1_rc": orf1rc, "orf2_rc": orf2rc, "orf3_rc": orf3rc}
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

    if input_type == "transscript":
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
                dna_end = dna_start + wanted_len * 3
                dna_start = full_orf_len * 3 - ((wanted_len + 1) * 3)
            elif orf_label == "orf2rc":
                dna_start = (pos_orf * 3) + 2
                dna_end = dna_start + (wanted_len * 3) + 2
            elif orf_label == "orf3rc":
                dna_start = (pos_orf * 3) + 2
                dna_end = dna_start + (wanted_len * 3) + 2
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


if input_type == "all":
    alloutput = open(output_name, "w")
    records = map(prot_record_solo, SeqIO.parse(input_name, "fasta"))
    SeqIO.write(records, "translation_6.fasta", "fasta")
else:
    records = map(prot_record, SeqIO.parse(input_name, "fasta"))
    SeqIO.write(records, output_name, "fasta")
