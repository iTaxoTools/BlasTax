import os
import shutil
import subprocess
from pathlib import Path
from typing import Literal

from utils import complement, translate


def get_blast_env() -> dict:
    here = Path(__file__).parent
    bin = here / "bin"
    env = os.environ.copy()
    env["PATH"] += f"{os.pathsep}{bin}"
    return env


BLAST_ENV = get_blast_env()


def make_database(
    input_path: str,
    output_path: str,
    type: Literal["nucl", "prot"],
    name: str,
) -> bool:
    p = subprocess.Popen(
        "makeblastdb -parse_seqids -in "
        + input_path
        + " -dbtype "
        + type
        + " -title "
        + name
        + " -out "
        + output_path,
        + " -blastdb_version 4",
        shell=True,
        stdout=subprocess.PIPE,
        env=BLAST_ENV,
    )
    p.wait()

    return bool(p.returncode == 0)


def run_blast(
    blast_binary: str,
    query_path: Path | str,
    database_path: Path | str,
    output_path: Path | str,
    evalue: str,
    num_threads: int,
    outfmt: str,
    other: str,
) -> bool:
    command = (
        f"{blast_binary} -query {str(query_path)} -db {str(database_path)} -out {str(output_path)} "
        f"-evalue {evalue} -num_threads {num_threads} -outfmt {outfmt} {other}"
    )

    p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, env=BLAST_ENV)
    p.wait()

    return bool(p.returncode == 0)


def run_blast_align(
    blast_binary: str,
    query_path: Path | str,
    database_path: Path | str,
    output_path: Path | str,
    evalue: str,
    num_threads: int,
    verbose: bool = True,
) -> bool:
    command = (
        f"{blast_binary} -out {output_path} -query {query_path} -outfmt '{int(6)} length pident qseqid sseqid sseq qframe sframe' "
        f"-evalue {evalue} -db {database_path} -num_threads {num_threads}"
    )

    p = subprocess.Popen(
        command,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=BLAST_ENV,
    )
    p.wait()

    if verbose:
        stdout, stderr = p.communicate()
        stdout = stdout.decode("utf-8")
        stderr = stderr.decode("utf-8")

        print("\nBLAST Standard Output:")
        print(stdout)
        print("\nBLAST Standard Error:")
        print(stderr)
        print(f"\nBLAST Return Code: {p.returncode}")

    return bool(p.returncode == 0)


def blastx_parse(
    input_path: Path | str,
    blast_result_path: Path | str,
    output_path: Path | str,
    extra_nucleotide_path: Path | str,
    database_name: str,
):
    infile = open(input_path, "r")
    infile2 = open(extra_nucleotide_path, "r")
    resultfile = open(blast_result_path, "r")
    outfile = open(output_path, "w")

    # Query-Sequences into output file
    for line in infile:
        outfile.write(line)

    sseqid_list = []
    for line in resultfile:
        splitti = line.split("\t")
        sseqid_list.append(splitti[3])
    name_list = []
    for eintrag in sseqid_list:
        # elem=eintrag.split('|')
        # print(elem[2])
        name_list.append(eintrag)
    ns_list = []
    labels = []
    for nam in name_list:
        nam_split = nam.split("_")
        if nam_split[0] in ns_list:
            labels.append(nam_split[0])
        ns_list.append(nam_split[0])

    resultfile.close()
    resultfile = open(blast_result_path, "r")

    infile.close()
    infile = open(input_path, "a")
    # de-duplication
    dict_53_added = {}
    dict_35_added = {}
    # good hits are appended to the query sequences
    for line in resultfile:
        #        print("BLAST OUTPUT LINE: ", line)
        splitti = line.split("\t")
        pident = splitti[1]
        #        print("SPLITTI 3: ", splitti[3])
        if (float(pident) >= 70.0) and (float(splitti[0]) >= 100.0):
            infile2 = open(extra_nucleotide_path, "r")
            for line2 in infile2:
                # Added. needed to be checked
                line2 = line2.replace(" ", "_")
                #                print("ADDITIONAL FILE LINE: ", line2)
                if splitti[3] in line2:
                    seq = infile2.readline()
                    print(seq)
            infile2.close()
            #            outfile.write('>' + db_name + '_' + splitti[3] + '_' + 'pident' + '_' + pident[:-2] + '\n')
            #            outfile.write(seq + '\n')
            if (len(seq) % 3) != 0:
                print("len", len(seq), seq)
            erg = translate(seq)
            r53 = erg[0:3]
            r35 = erg[3:]
            print("auftei", erg)
            print("auftei", r53, r35)

            for orient in r53:
                index = orient.find(splitti[4])
                print("ori", len(orient), len(splitti[4]), orient, index, splitti[4])
                if index >= 0:
                    # Determine the offset based on index
                    offset = index * 3 if index == 0 else (index * 3) + 1

                    # Prepare unique keys for dict_53_added
                    shorter_pident = f">{database_name}_{splitti[3]}_pident_"
                    head_pident53_added = (
                        f">{database_name}_{splitti[3]}_pident_{pident[:-2]}\n"
                    )
                    head_seq53_added = (
                        seq[offset : ((len(splitti[4]) * 3) + offset)] + "\n"
                    )
                    any_key_starting_with_prefix = next(
                        (
                            key
                            for key in dict_53_added
                            if key.startswith(shorter_pident)
                        ),
                        None,
                    )
                    #                    print("HEADER SHORT: ", shorter_pident)
                    #                    print("HEADER: ", head_pident53_added)
                    #                    print("SEQUENCE: ", head_seq53_added)
                    #                    print("HEADER FROM DICT: ", any_key_starting_with_prefix)

                    if any_key_starting_with_prefix:
                        existing_seq_length = len(
                            dict_53_added[any_key_starting_with_prefix]
                        )
                        new_seq_length = len(head_seq53_added)
                        #                        print("SEQ LENGTHS: ", existing_seq_length, "\t", new_seq_length)
                        if new_seq_length > existing_seq_length:
                            dict_53_added.pop(any_key_starting_with_prefix, None)
                            dict_53_added[head_pident53_added] = head_seq53_added
                        elif new_seq_length == existing_seq_length:
                            old_pident53 = float(
                                any_key_starting_with_prefix.split("_")[-1].rstrip()
                            )
                            new_pident53 = float(
                                head_pident53_added.split("_")[-1].rstrip()
                            )
                            #                            print("OLD PIDENT: ", old_pident53)
                            #                            print("NEW PIDENT: ", new_pident53)
                            if new_pident53 > old_pident53:
                                dict_53_added.pop(any_key_starting_with_prefix, None)
                                dict_53_added[head_pident53_added] = head_seq53_added
                        else:
                            continue
                    else:
                        dict_53_added[head_pident53_added] = head_seq53_added

            for orient in r35:
                index = orient.find(splitti[4])
                print("ori", len(orient), len(splitti[4]), orient, index, splitti[4])
                if index > 0:
                    offset = (index * 3) + 1
                elif index == 0:
                    offset = index * 3
                if index >= 0:
                    compiseq = complement(seq)
                    fragment = compiseq[offset : ((len(splitti[4]) * 3) + offset)]
                    revcompseq = fragment[::-1]
                    # deduplication
                    shorter_pident = f">{database_name}_{splitti[3]}_pident_"
                    head_pident35_added = (
                        f">{database_name}_{splitti[3]}_pident_{pident[:-2]}\n"
                    )
                    head_seq35_added = revcompseq + "\n"
                    any_key_starting_with_prefix = next(
                        (
                            key
                            for key in dict_35_added
                            if key.startswith(shorter_pident)
                        ),
                        None,
                    )

                    if any_key_starting_with_prefix:
                        existing_seq_length = len(
                            dict_35_added[any_key_starting_with_prefix]
                        )
                        new_seq_length = len(head_seq35_added)
                        #                        print("SEQ LENGTHS: ", existing_seq_length, "\t", new_seq_length)
                        if new_seq_length > existing_seq_length:
                            dict_35_added.pop(any_key_starting_with_prefix, None)
                            #                            print("The sequence was removed: ", removed_value)
                            dict_35_added[head_pident35_added] = head_seq35_added
                        elif new_seq_length == existing_seq_length:
                            old_pident35 = float(
                                any_key_starting_with_prefix.split("_")[-1].rstrip()
                            )
                            new_pident35 = float(
                                head_pident35_added.split("_")[-1].rstrip()
                            )
                            #                            print("OLD PIDENT: ", old_pident53)
                            #                            print("NEW PIDENT: ", new_pident53)
                            if new_pident35 > old_pident35:
                                dict_35_added.pop(any_key_starting_with_prefix, None)
                                #                                print("The sequence was removed: ", removed_value)
                                dict_35_added[head_pident35_added] = head_seq35_added
                        else:
                            continue
                    else:
                        dict_35_added[head_pident35_added] = head_seq35_added

    for header, sequence in dict_53_added.items():
        outfile.write(f"{header}{sequence}")
    for header, sequence in dict_35_added.items():
        outfile.write(f"{header}{sequence}")

    infile.close()
    outfile.close()
    resultfile.close()


def blastn_parse(
    input_path: Path | str,
    blast_result_path: Path | str,
    output_path: Path | str,
    database_name: str,
):
    # copy the content of the input file to a new output file
    blastfile = open(blast_result_path, "r")
    try:
        shutil.copyfile(input_path, output_path)
        print(f"Content of {input_path} copied to {output_path} successfully.")
    except IOError as e:
        print(f"Error: {e}")
    # add upp blast hits to the new output file
    outfile = open(output_path, "a")
    dict_head_pident = {}
    dict_head_seq = {}
    for line in blastfile:
        splitti = line.split("\t")
        print(splitti, splitti[3])
        pident = splitti[1]
        sequence_line = f"{splitti[4]}\n"
        short_header = f">{database_name}_{splitti[3]}"

        if short_header in dict_head_seq:
            old_seqlen = len(dict_head_seq[short_header])
            old_pident = dict_head_pident[short_header]
            if len(sequence_line) > old_seqlen:
                dict_head_pident[short_header] = pident[:-2]
                dict_head_seq[short_header] = sequence_line
            elif pident[:-2] > old_pident:
                dict_head_pident[short_header] = pident[:-2]
                dict_head_seq[short_header] = sequence_line
            else:
                continue

        else:
            dict_head_pident[short_header] = pident[:-2]
            dict_head_seq[short_header] = sequence_line
    #                list_of_headers.append(short_header)

    #            outfile.writelines([header_line, sequence_line])
    outfile.write("\n")
    for header, sequence in zip(dict_head_pident.keys(), dict_head_seq.values()):
        outfile.write(f"{header}_pident_{dict_head_pident[header]}\n{sequence}")

    outfile.close()
    blastfile.close()


def museoscript_original_reads(
    blast_path: Path | str,
    original_query_path: Path | str,
    output_path: Path | str,
    pident_threshold: float,
):
    with open(original_query_path, "r") as org_query:
        query_list = org_query.readlines()

    with open(blast_path, "r") as blast:
        with open(output_path, "w") as museo:
            for line in blast:
                splitti = line.split("\t")
                pident = splitti[4]
                header = splitti[0]
                if float(pident) >= pident_threshold:
                    for i, element in enumerate(query_list):
                        if header in element:
                            museo.write(f">{splitti[0]}_{splitti[1]}_{pident}\n")
                            museo.write(query_list[i + 1])


def museoscript_parse(
    blast_path: Path | str,
    output_path: Path | str,
    pident_threshold: float,
):
    with open(blast_path, "r") as blast:
        with open(output_path, "w") as museo:
            for line in blast:
                splitti = line.split("\t")
                pident = splitti[4]

                if float(pident) >= pident_threshold:
                    sequence_line = f"{splitti[5]}"
                    header = f">{splitti[0]}_{splitti[1]}_{pident}\n"
                    museo.write(header)
                    museo.write(sequence_line)
