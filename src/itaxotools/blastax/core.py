import shutil
import string
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Literal

from itaxotools.taxi2.handlers import FileHandler
from itaxotools.taxi2.sequences import Sequence, SequenceHandler

from .blast import command_to_args, execute_blast_command, get_blast_binary
from .utils import complement, string_trimmer, translate


def make_database(
    input_path: str,
    output_path: str,
    type: Literal["nucl", "prot"],
    name: str,
    version: Literal[4, 5] = 4,
):
    output_pattern = Path(output_path) / name
    args = [
        get_blast_binary("makeblastdb"),
        "-parse_seqids",
        "-in",
        input_path,
        "-title",
        name,
        "-out",
        str(output_pattern),
        "-dbtype",
        type,
        "-blastdb_version",
        str(version),
    ]
    execute_blast_command(args)


def run_blast(
    blast_binary: str,
    query_path: Path | str,
    database_path: Path | str,
    output_path: Path | str,
    evalue: str,
    num_threads: int,
    outfmt: str,
    other: str,
):
    command = (
        f"{get_blast_binary(blast_binary)} -query '{str(query_path)}' -db '{str(database_path)}' -out '{str(output_path)}' "
        f"-evalue {evalue} -num_threads {num_threads} -outfmt '{outfmt}' {other}"
    )
    args = command_to_args(command)
    execute_blast_command(args)


def run_blast_align(
    blast_binary: str,
    query_path: Path | str,
    database_path: Path | str,
    output_path: Path | str,
    evalue: str,
    num_threads: int,
):
    return run_blast(
        blast_binary=blast_binary,
        query_path=query_path,
        database_path=database_path,
        output_path=output_path,
        evalue=evalue,
        num_threads=num_threads,
        outfmt="6 length pident qseqid sseqid sseq qframe sframe",
        other="",
    )


def run_blast_decont(
    blast_binary: str,
    query_path: Path | str,
    database_path: Path | str,
    output_path: Path | str,
    evalue: str,
    num_threads: int,
):
    return run_blast(
        blast_binary=blast_binary,
        query_path=query_path,
        database_path=database_path,
        output_path=output_path,
        evalue=evalue,
        num_threads=num_threads,
        outfmt="6 qseqid sseqid pident bitscore length",
        other="",
    )


def blastx_parse(
    input_path: Path | str,
    blast_result_path: Path | str,
    output_path: Path | str,
    extra_nucleotide_path: Path | str,
    database_name: str,
    all_matches: bool = False,
    pident_arg: float = 70.0,
    length_arg: int = 100,
    user_spec_name: str = None,
):
    infile = open(input_path, "r")
    infile2 = open(extra_nucleotide_path, "r")
    resultfile = open(blast_result_path, "r")
    outfile = open(output_path, "w")

    # modify the user_spec_name
    if user_spec_name is not None:
        if not user_spec_name.startswith(">"):
            user_spec_name = ">" + user_spec_name

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
        if (float(pident) >= pident_arg) and (int(splitti[0]) >= length_arg):
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
                    head_pident53_added = f">{database_name}_{splitti[3]}_pident_{pident[:-2]}\n"
                    head_seq53_added = seq[offset : ((len(splitti[4]) * 3) + offset)] + "\n"
                    any_key_starting_with_prefix = next(
                        (key for key in dict_53_added if key.startswith(shorter_pident)),
                        None,
                    )
                    #                    print("HEADER SHORT: ", shorter_pident)
                    #                    print("HEADER: ", head_pident53_added)
                    #                    print("SEQUENCE: ", head_seq53_added)
                    #                    print("HEADER FROM DICT: ", any_key_starting_with_prefix)
                    if all_matches:
                        # Include all hitted sequences in dict_53_added
                        dict_53_added[head_pident53_added] = head_seq53_added
                    else:
                        if any_key_starting_with_prefix:
                            existing_seq_length = len(dict_53_added[any_key_starting_with_prefix])
                            new_seq_length = len(head_seq53_added)
                            #                        print("SEQ LENGTHS: ", existing_seq_length, "\t", new_seq_length)
                            if new_seq_length > existing_seq_length:
                                dict_53_added.pop(any_key_starting_with_prefix, None)
                                dict_53_added[head_pident53_added] = head_seq53_added
                            elif new_seq_length == existing_seq_length:
                                old_pident53 = float(any_key_starting_with_prefix.split("_")[-1].rstrip())
                                new_pident53 = float(head_pident53_added.split("_")[-1].rstrip())
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
                    head_pident35_added = f">{database_name}_{splitti[3]}_pident_{pident[:-2]}\n"
                    head_seq35_added = revcompseq + "\n"
                    any_key_starting_with_prefix = next(
                        (key for key in dict_35_added if key.startswith(shorter_pident)),
                        None,
                    )
                    if all_matches:
                        # Include all hitted sequences in dict_35_added
                        dict_35_added[head_pident35_added] = head_seq35_added
                    else:
                        if any_key_starting_with_prefix:
                            existing_seq_length = len(dict_35_added[any_key_starting_with_prefix])
                            new_seq_length = len(head_seq35_added)
                            #                        print("SEQ LENGTHS: ", existing_seq_length, "\t", new_seq_length)
                            if new_seq_length > existing_seq_length:
                                dict_35_added.pop(any_key_starting_with_prefix, None)
                                #                            print("The sequence was removed: ", removed_value)
                                dict_35_added[head_pident35_added] = head_seq35_added
                            elif new_seq_length == existing_seq_length:
                                old_pident35 = float(any_key_starting_with_prefix.split("_")[-1].rstrip())
                                new_pident35 = float(head_pident35_added.split("_")[-1].rstrip())
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
        if user_spec_name is not None:
            outfile.write(f"{user_spec_name}\n{sequence}")
        else:
            outfile.write(f"{header}{sequence}")
    for header, sequence in dict_35_added.items():
        if user_spec_name is not None:
            outfile.write(f"{user_spec_name}\n{sequence}")
        else:
            outfile.write(f"{header}{sequence}")

    infile.close()
    outfile.close()
    resultfile.close()


def blast_parse(
    input_path: Path | str,
    blast_result_path: Path | str,
    output_path: Path | str,
    database_name: str,
    all_matches: bool = False,
    pident_arg: float = None,
    length_arg: int = None,
    user_spec_name: str = None,
    append_only: bool = False,
):
    # modify the user_spec_name
    if user_spec_name is not None:
        if not user_spec_name.startswith(">"):
            user_spec_name = ">" + user_spec_name
    # copy the content of the input file to a new output file
    blastfile = open(blast_result_path, "r")
    if not append_only:
        shutil.copyfile(input_path, output_path)
    # add upp blast hits to the new output file
    outfile = open(output_path, "a")
    outfile.write("\n")
    # to keep multiple hits per query file but with unique seqid
    if all_matches:
        dict_head_pident = {}
        dict_head_seq = {}
        for line in blastfile:
            splitti = line.split("\t")
            pident = float(splitti[1])
            sequence = f"{splitti[4]}\n"
            short_header = f">{database_name}_{splitti[3]}"
            # keep track for the seqid to keep only unique seqid
            if short_header in dict_head_seq:
                old_seqlen = len(dict_head_seq[short_header])
                old_pident = dict_head_pident[short_header]
                if len(sequence) > old_seqlen:
                    dict_head_pident[short_header] = pident
                    dict_head_seq[short_header] = sequence
                elif pident > old_pident:
                    dict_head_pident[short_header] = pident
                    dict_head_seq[short_header] = sequence
                else:
                    continue
            # check whether a hit fulfills requirements to be added to the dictionary with unique seID
            else:
                if pident_arg is not None and length_arg is not None:
                    if pident >= pident_arg and len(sequence) - 1 >= length_arg:
                        dict_head_pident[short_header] = pident
                        dict_head_seq[short_header] = sequence
                elif pident_arg is not None:
                    if pident > pident_arg:
                        dict_head_pident[short_header] = pident
                        dict_head_seq[short_header] = sequence
                elif length_arg is not None:
                    if len(sequence) - 1 >= length_arg:
                        dict_head_pident[short_header] = pident
                        dict_head_seq[short_header] = sequence
                else:
                    dict_head_pident[short_header] = pident
                    dict_head_seq[short_header] = sequence

        for header, sequence in zip(dict_head_pident.keys(), dict_head_seq.values()):
            if user_spec_name is not None:
                outfile.write(f"{user_spec_name}\n{sequence}")
            else:
                pident_str = f"{dict_head_pident[header]:.4f}"[:-1]
                outfile.write(f"{header}_pident_{pident_str}\n{sequence}")
    # to keep just one hit per query file
    else:
        max_seq_len = 0
        for line in blastfile:
            splitti = line.split("\t")
            pident = float(splitti[1])
            sequence_line = f"{splitti[4]}\n"
            header = f">{database_name}_{splitti[3]}"
            if len(sequence_line) > max_seq_len:
                max_seq_len = len(sequence_line)
                final_header = header
                final_sequence_line = sequence_line
                final_pident = pident

        if max_seq_len:
            if user_spec_name is not None:
                outfile.write(f"{user_spec_name}\n{final_sequence_line}")
            else:
                pident_str = f"{final_pident:.4f}"[:-1]
                outfile.write(f"{final_header}_pident_{pident_str}\n{final_sequence_line}")

    outfile.close()
    blastfile.close()


def museoscript(
    blast_path: Path | str,
    output_path: Path | str,
    original_reads_path: Path | None = None,
    pident_threshold: float = 0.9,
    deduplicate: float = True,
):
    sequences: dict[str, dict[str, str]] = defaultdict(dict)
    pidents: dict[str, dict[str, str]] = defaultdict(dict)

    with FileHandler.Tabfile(blast_path) as blast_file:
        for line in blast_file:
            query_id = line[0]
            reference_id = line[1]
            pident = line[4]
            sequence = line[5]
            if float(pident) >= pident_threshold:
                if deduplicate and pidents[query_id]:
                    old_pident = next(iter(pidents[query_id].values()))
                    if pident >= old_pident:
                        continue
                    sequences[query_id] = {}
                    pidents[query_id] = {}
                sequences[query_id][reference_id] = sequence
                pidents[query_id][reference_id] = pident

    if original_reads_path is not None:
        with SequenceHandler.Fasta(original_reads_path) as original_file:
            for original in original_file:
                for query_id in sequences:
                    if original.id.startswith(query_id):
                        for reference_id in sequences[query_id]:
                            sequences[query_id][reference_id] = original.seq
                        break

    with SequenceHandler.Fasta(output_path, "w", line_width=0) as museo_file:
        for query_id in sequences:
            for reference_id in sequences[query_id]:
                sequence = sequences[query_id][reference_id]
                pident = pidents[query_id][reference_id]
                header = f"{query_id}_{reference_id}_{pident}"
                museo_file.write(Sequence(header, sequence))


def _get_decont_hits_dict(
    path: Path | str,
    column: int,
) -> dict[str, float]:
    hits: dict[str, float] = {}
    with FileHandler.Tabfile(path) as file:
        for item in file:
            id = item[0]
            value = float(item[column])
            if id not in hits or hits[id] < value:
                hits[id] = value
    return hits


def decontaminate(
    query_path: Path | str,
    blasted_ingroup_path: Path | str,
    blasted_outgroup_path: Path | str,
    ingroup_sequences_path: Path | str,
    outgroup_sequences_path: Path | str,
    column: int,
):
    ingroup_hits = _get_decont_hits_dict(blasted_ingroup_path, column)
    outgroup_hits = _get_decont_hits_dict(blasted_outgroup_path, column)

    with (
        SequenceHandler.Fasta(query_path) as query_file,
        SequenceHandler.Fasta(ingroup_sequences_path, "w", line_width=0) as ingroup_file,
        SequenceHandler.Fasta(outgroup_sequences_path, "w", line_width=0) as outgroup_file,
    ):
        for item in query_file:
            ingroup_hit = ingroup_hits.get(item.id, -1)
            outgroup_hit = outgroup_hits.get(item.id, -1)
            if ingroup_hit >= outgroup_hit:
                ingroup_file.write(item)
            else:
                outgroup_file.write(item)


def get_timestamp_suffix(timestamp: datetime) -> str:
    return timestamp.strftime(r"_%Y%m%dT%H%M%S")


def get_info_suffix(**kwargs) -> str:
    info = ""
    for key, value in kwargs.items():
        if value is None:
            info += f"_{str(key)}"
        else:
            info += f"_{str(key)}_{str(value)}"
    return info


def get_blast_filename(
    input_path: Path,
    outfmt: int = 0,
    timestamp: datetime | None = None,
    **kwargs,
) -> str:
    suffix = {
        0: ".txt",
        1: ".txt",
        2: ".txt",
        3: ".txt",
        4: ".txt",
        5: ".xml",
        6: ".tsv",
        7: ".tsv",
        8: ".asn1",
        9: ".bin",
        10: ".csv",
        11: ".asn1",
        12: ".json",
        13: ".json",
        14: ".xml",
        15: ".json",
        16: ".xml",
        17: ".sam",
        18: ".txt",
    }.get(outfmt, ".out")
    path = input_path.with_suffix(suffix)

    info = get_info_suffix(**kwargs)
    path = path.with_stem(path.stem + info)

    if timestamp is not None:
        strftime = get_timestamp_suffix(timestamp)
        path = path.with_stem(path.stem + strftime)
    return path.name


def get_output_filename(
    input_path: Path,
    suffix: str | None = None,
    description: str | None = None,
    timestamp: datetime | None = None,
    **kwargs,
) -> str:
    path = input_path
    if suffix:
        # provided suffix must include the dot
        path = path.with_suffix(suffix)
    if description:
        path = path.with_stem(path.stem + "_" + description)
    if kwargs:
        info = get_info_suffix(**kwargs)
        path = path.with_stem(path.stem + info)
    if timestamp:
        strftime = get_timestamp_suffix(timestamp)
        path = path.with_stem(path.stem + strftime)
    return path.name


def get_append_filename(
    input_path: Path,
    timestamp: datetime | None = None,
    **kwargs,
) -> str:
    return get_output_filename(
        input_path=input_path,
        suffix=".fasta",
        description="with_blast_matches",
        timestamp=timestamp,
        **kwargs,
    )


def get_museo_filename(
    input_path: Path,
    timestamp: datetime | None = None,
    **kwargs,
) -> str:
    return get_output_filename(
        input_path=input_path,
        suffix=".fasta",
        description="museo",
        timestamp=timestamp,
        **kwargs,
    )


def get_decont_blast_filename(
    input_path: Path,
    description: Literal["ingroup", "outgroup"],
    timestamp: datetime | None = None,
    **kwargs,
) -> str:
    path = input_path.with_stem(input_path.stem + f"_{description}")
    return get_blast_filename(path, outfmt=6, timestamp=timestamp, **kwargs)


def get_decont_sequences_filename(
    input_path: Path,
    description: Literal["decontaminated", "contaminants"],
    timestamp: datetime | None = None,
    **kwargs,
) -> str:
    return get_output_filename(
        input_path=input_path,
        suffix=".fasta",
        description=description,
        timestamp=timestamp,
        **kwargs,
    )


def get_fasta_prepared_filename(
    input_path: Path,
    timestamp: datetime | None = None,
) -> str:
    return get_output_filename(
        input_path=input_path,
        suffix=".fasta",
        description="prepared",
        timestamp=timestamp,
    )


def get_error_filename(
    input_path: Path,
    timestamp: datetime | None = None,
) -> str:
    return get_output_filename(
        input_path=input_path,
        suffix=".log",
        description="errors",
        timestamp=timestamp,
    )


# Fasta sequence name modifier
def fasta_name_modifier(
    input_name: Path | str,
    output_name: Path | str,
    trim: bool,
    add: bool,
    replace: bool,
    sanitize: bool,
    preserve_separators: bool,
    trimposition: str,
    trimmaxchar: int,
    renameauto: bool,
    direc: str = None,
    addstring: str = None,
    findstring: str = None,
    replacestring: str = None,
    fixseqspaces: bool = False,
    fixseqasterisks: bool = False,
    fixaliseparator: bool = False,
):
    letters_and_numbers = string.ascii_letters + string.digits + ">_"
    if preserve_separators:
        letters_and_numbers += "@|"

    seqtrans = {}
    idtrans = {}
    if fixseqspaces:
        seqtrans |= str.maketrans(" ", "-")
    if fixseqasterisks:
        seqtrans |= str.maketrans("*", "-")
    if fixaliseparator:
        idtrans |= str.maketrans("@", "|")

    counter = 1
    sequence = ""

    with open(input_name, "r", encoding="utf-8", errors="surrogateescape") as file:
        with open(output_name, "w", encoding="utf-8") as outfile:
            for line in file:
                line = line.strip("\r\n")
                if not line:
                    continue
                elif line.startswith(";") or line.startswith("#"):
                    # ignore comment lines and ALI headers
                    continue
                elif ">" in line:
                    if sequence:
                        sequence = sequence.translate(seqtrans)
                        outfile.write(sequence + "\n")
                        sequence = ""
                    identifier = string_trimmer(
                        komm_zeile=line,
                        counter=counter,
                        trim=trim,
                        add=add,
                        replace=replace,
                        sanitize=sanitize,
                        trimpos=trimposition,
                        trimmaxchar=trimmaxchar,
                        auto=renameauto,
                        letters_and_numbers=letters_and_numbers,
                        direc=direc,
                        addstring=addstring,
                        findstring=findstring,
                        replacestring=replacestring,
                    )
                    identifier = identifier.translate(idtrans)
                    outfile.write(identifier + "\n")
                    counter += 1
                else:
                    sequence += line
            if sequence:
                sequence = sequence.translate(seqtrans)
                outfile.write(sequence + "\n")

    outfile.close()
