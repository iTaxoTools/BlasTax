#!/usr/bin/env python3

import argparse
import gzip
import os
import sys
import tkinter as tk
import tkinter.filedialog as tkfiledialog
import tkinter.font as tkfont
import tkinter.messagebox
import tkinter.ttk as ttk
import warnings
from typing import BinaryIO, Iterator, List, Optional, TextIO, cast

from fastutils import (
    Pattern,
    fasta_iter,
    fasta_iter_chunks,
    fastq_iter,
    fastq_iter_chunks,
    make_template,
    parse_pattern_optional,
    template_files,
)


def parse_size(s: str) -> Optional[int]:
    """
    Parses file size as number with a suffix in "bBkKmMgG", interpreted as a unit
    """
    num = s[:-1]
    suffix = s[-1]
    try:
        power = dict(b=0, k=1, m=2, g=3)[suffix.casefold()]
    except KeyError:
        return None
    return round(float(num) * (1024**power))


def list_bytes(chunk: List[str]) -> bytes:
    """
    converts a list of string into utf-8 encoded bytes
    """
    return b"".join(map(lambda s: bytes(s, "utf-8"), chunk))


def write_maxsize(chunks: Iterator[List[str]], maxsize: int, compressed: bool, output_template: str) -> None:
    """
    Writes chunks to the files based on the output_template, each file will be no bigger than maxsize.
    Each chunk will be written whole in some file.
    If 'compressed' each file will be compressed with gzip.
    """
    # generator of output files
    files = template_files(output_template, "wb", compressed)
    # keep track of written size
    current_size = 0
    # current output file
    current_file = cast(BinaryIO, next(files))

    for chunk in chunks:
        # convert the chunk into bytes
        bytes_to_write = list_bytes(chunk)
        if current_size + len(bytes_to_write) > maxsize:
            # if the current file would overflow, switch to a new file
            current_file = cast(BinaryIO, next(files))
            current_size = 0
        # write the bytes and add the written size
        current_file.write(bytes_to_write)
        current_size = current_size + len(bytes_to_write)
    # close the last file
    try:
        files.send("stop")
    except StopIteration:
        pass


def fastsplit(
    file_format: str,
    split_n: Optional[int],
    maxsize: Optional[int],
    seqid_pattern: Optional[str],
    sequence_pattern: Optional[str],
    infile_path: Optional[str],
    compressed: bool,
    outfile_template: Optional[str],
) -> None:
    if not infile_path:
        # raise error, if there is no input file
        raise ValueError("No input file")
    if infile_path.endswith(".gz"):
        infile = cast(TextIO, gzip.open(infile_path, mode="rt", errors="replace"))
    else:
        infile = open(infile_path, errors="replace")
    with infile:
        # prepare a valid output template
        if not outfile_template:
            outfile_template = make_template(infile_path)
        elif "#" not in outfile_template:
            outfile_template = make_template(outfile_template)
        if maxsize or split_n:
            # initialize the input file reader
            if file_format == "fasta":
                chunks = fasta_iter_chunks(infile)
            elif file_format == "fastq":
                chunks = fastq_iter_chunks(infile)
            elif file_format == "text":
                chunks = map(lambda s: [s], infile)
            else:
                chunks = None
        else:
            chunks = None
        # call subfunctions
        if maxsize:
            # split by maximum size
            assert chunks is not None
            write_maxsize(chunks, maxsize, compressed, outfile_template)
        elif split_n:
            # split by number of files
            # get the size of the input
            size = os.stat(infile_path).st_size
            # if split_n == 6, size == 42 gives maxsize == 7, size == 43 gives maxsize == 8, size 48 gives maxsize 8
            maxsize = (size - 1 + split_n) // split_n
            assert chunks is not None
            write_maxsize(chunks, maxsize, compressed, outfile_template)
        elif seqid_pattern or sequence_pattern:
            # split by patterns
            if file_format == "fasta":
                fastsplit_fasta_filter(
                    infile,
                    parse_pattern_optional(seqid_pattern),
                    parse_pattern_optional(sequence_pattern),
                    compressed,
                    outfile_template,
                )
            elif file_format == "fastq":
                fastsplit_fastq_filter(
                    infile,
                    parse_pattern_optional(seqid_pattern),
                    parse_pattern_optional(sequence_pattern),
                    compressed,
                    outfile_template,
                )
            else:
                raise ValueError("Pattern are not supported for text files")


def fastsplit_fasta_filter(
    infile: TextIO,
    seqid_pattern: Optional[Pattern],
    sequence_pattern: Optional[Pattern],
    compressed: bool,
    outfile_template: str,
) -> None:
    """
    splits a fasta file by patterns
    """
    # creates a function to open output files
    if compressed:

        def opener(name: str) -> TextIO:
            return cast(TextIO, gzip.open(name, mode="wt", errors="replace"))
    else:

        def opener(name: str) -> TextIO:
            return open(name, mode="w", errors="replace")

    # assemples names and open output files
    accepted_file, rejected_file = map(
        opener, map(lambda s: outfile_template.replace("#", s), ["_accepted", "_rejected"])
    )
    # create the records' stream
    records = fasta_iter(infile)
    # warn about the line breaks
    line_breaks_warned = False
    for seqid, sequence in records:
        if not line_breaks_warned and sequence_pattern and len(sequence) > 1:
            line_breaks_warned = True
            warnings.warn(
                f"The file {infile.name} contains sequences interrupted with line breaks, and the search for sequence motifs will not work reliably in this case - some sequences with the specified motif will likely be missed. Please first transform your file into a fasta file without line breaks interrupting the sequences."
            )
        # calculate of the record matches the pattern
        accepted = (seqid_pattern and seqid_pattern.match(seqid)) or (
            sequence_pattern and any(map(sequence_pattern.match, sequence))
        )
        # choose the output file
        if accepted:
            output = accepted_file
        else:
            output = rejected_file
        # write the record to the selected file
        output.write(seqid)
        for chunk in sequence:
            output.write(chunk)


def fastsplit_fastq_filter(
    infile: TextIO,
    seqid_pattern: Optional[Pattern],
    sequence_pattern: Optional[Pattern],
    compressed: bool,
    outfile_template: str,
) -> None:
    """
    splits a fastq file by patterns
    """
    # creates a function to open output files
    if compressed:

        def opener(name: str) -> TextIO:
            return cast(TextIO, gzip.open(name, mode="wt", errors="replace"))
    else:

        def opener(name: str) -> TextIO:
            return open(name, mode="w", errors="replace")

    # assemples names and open output files
    accepted_file, rejected_file = map(
        opener, map(lambda s: outfile_template.replace("#", s), ["_accepted", "_rejected"])
    )
    # create the records' stream
    records = fastq_iter(infile)
    for seqid, sequence, *quality in records:
        # calculate of the record matches the pattern
        accepted = (seqid_pattern and seqid_pattern.match(seqid)) or (
            sequence_pattern and sequence_pattern.match(sequence)
        )
        # choose the output file
        if accepted:
            output = accepted_file
        else:
            output = rejected_file
        # write the record to the selected file
        for line in [seqid, sequence, *quality]:
            output.write(line)


def launch_gui() -> None:
    # the base of the gui
    root = tk.Tk()
    root.title("Fastsplit")
    if os.name == "nt":
        root.wm_iconbitmap(os.path.join("data", "Fastsplit_icon.ico"))
    mainframe = ttk.Frame(root, padding=5)
    top_frame = ttk.Frame(mainframe, padding="0 0 0 5")
    middle_frame = ttk.Frame(mainframe)
    bottom_frame = ttk.Frame(mainframe)
    style = ttk.Style()
    style.configure("SplitButton.TButton", background="blue")

    # create labels
    infile_lbl = ttk.Label(top_frame, text="Input file")
    outfile_lbl = ttk.Label(top_frame, text="Output files' template")
    pattern_hint_lbl = ttk.Label(mainframe, text="\t¹The search words should be in double quotes")

    # create the entries
    infile_var = tk.StringVar()
    infile_entry = ttk.Entry(top_frame, textvariable=infile_var)
    outfile_var = tk.StringVar()
    outfile_entry = ttk.Entry(top_frame, textvariable=outfile_var)
    maxsize_var = tk.StringVar()
    maxsize_entry = ttk.Entry(bottom_frame, textvariable=maxsize_var, validate="key")
    split_n_var = tk.StringVar()
    split_n_entry = ttk.Entry(bottom_frame, textvariable=split_n_var, validate="key")
    seqid_pattern_var = tk.StringVar()
    seqid_pattern_entry = ttk.Entry(bottom_frame, textvariable=seqid_pattern_var)
    sequence_pattern_var = tk.StringVar()
    sequence_pattern_entry = ttk.Entry(bottom_frame, textvariable=sequence_pattern_var)

    # validation for maxsize and split_n entries
    def validate_numbers() -> bool:
        maxsize = maxsize_var.get()
        split_n = split_n_var.get()
        return (not maxsize or maxsize.isnumeric()) or (not split_n or split_n.isnumeric())

    # set the validation
    maxsize_entry.configure(validatecommand=validate_numbers)
    split_n_entry.configure(validatecommand=validate_numbers)

    # create the radiobuttons
    format_var = tk.StringVar(value="fasta")
    fasta_rbtn = ttk.Radiobutton(middle_frame, text="fasta", variable=format_var, value="fasta")
    fastq_rbtn = ttk.Radiobutton(middle_frame, text="fastq", variable=format_var, value="fastq")
    text_rbtn = ttk.Radiobutton(middle_frame, text="text", variable=format_var, value="text")
    option_var = tk.StringVar(value="maxsize")
    maxsize_rbtn = ttk.Radiobutton(bottom_frame, text="Maximum size", variable=option_var, value="maxsize")
    split_n_rbtn = ttk.Radiobutton(bottom_frame, text="Number of output files", variable=option_var, value="split_n")
    seqid_rbtn = ttk.Radiobutton(bottom_frame, text="Sequence identifier pattern¹", variable=option_var, value="seqid")
    sequence_rbtn = ttk.Radiobutton(bottom_frame, text="Sequence motif pattern¹", variable=option_var, value="sequence")

    def pattern_radio_buttons_state(name1: str, name2: str, op: str) -> None:
        if format_var.get() == "text":
            for widget in [seqid_rbtn, seqid_pattern_entry, sequence_rbtn, sequence_pattern_entry]:
                widget.configure(state="disabled")
        else:
            for widget in [seqid_rbtn, seqid_pattern_entry, sequence_rbtn, sequence_pattern_entry]:
                widget.configure(state="normal")

    format_var.trace_add("write", pattern_radio_buttons_state)

    # create the compress checkbutton
    compressed_var = tk.BooleanVar()
    compressed_checkbutton = ttk.Checkbutton(top_frame, text="Compress output", variable=compressed_var)

    # commands for the buttons
    def browse_infile() -> None:
        newpath: Optional[str] = tkfiledialog.askopenfilename()
        if newpath:
            try:
                newpath = os.path.relpath(newpath)
            except Exception:
                newpath = os.path.abspath(newpath)
            infile_var.set(newpath)

    def browse_outfile() -> None:
        newpath: Optional[str] = tkfiledialog.asksaveasfilename()
        if newpath:
            try:
                newpath = os.path.relpath(newpath)
            except Exception:
                newpath = os.path.abspath(newpath)
            outfile_var.set(newpath)

    def fastsplit_gui() -> None:
        maxsize = None
        split_n = None
        seqid_pattern = None
        sequence_pattern = None
        option = option_var.get()

        if option == "maxsize":
            maxsize = parse_size(maxsize_var.get())
        elif option == "split_n":
            split_n = int(split_n_var.get())
        elif option == "seqid":
            seqid_pattern = seqid_pattern_var.get()
        elif option == "sequence":
            sequence_pattern = sequence_pattern_var.get()

        try:
            # catch all warnings
            with warnings.catch_warnings(record=True) as warns:
                fastsplit(
                    format_var.get(),
                    split_n,
                    maxsize,
                    seqid_pattern,
                    sequence_pattern,
                    infile_var.get(),
                    compressed_var.get(),
                    outfile_var.get(),
                )
            # display the warnings generated during the conversion
            for w in warns:
                tkinter.messagebox.showwarning("Warning", str(w.message))
            # notify the user that the converions is finished
            tkinter.messagebox.showinfo("Done.", "The splitting has been completed")
        # show the ValueErrors and FileNotFoundErrors
        except ValueError as ex:
            tkinter.messagebox.showerror("Error", str(ex))
        except FileNotFoundError as ex:
            tkinter.messagebox.showerror("Error", str(ex))

    # create buttons
    infile_browse_btn = ttk.Button(top_frame, text="Browse", command=browse_infile)
    outfile_browse_btn = ttk.Button(top_frame, text="Browse", command=browse_outfile)
    split_btn = ttk.Button(top_frame, text="Split", command=fastsplit_gui, style="SplitButton.TButton")

    # populate the top frame
    logo_img = tk.PhotoImage(file=os.path.join(sys.path[0], "data", "iTaxoTools Digital linneaeus MICROLOGO.png"))
    ttk.Label(top_frame, image=logo_img).grid(row=0, column=3, rowspan=3, sticky="e")
    infile_lbl.grid(row=0, column=0, sticky="w")
    infile_entry.grid(row=1, column=0, sticky="we")
    infile_browse_btn.grid(row=1, column=1, sticky="w")
    outfile_lbl.grid(row=2, column=0, sticky="w")
    outfile_entry.grid(row=3, column=0, sticky="we")
    outfile_browse_btn.grid(row=3, column=1, sticky="w")
    split_btn.grid(row=3, column=3, sticky="e")
    compressed_checkbutton.grid(row=4, column=0, sticky="w")
    ttk.Label(top_frame).grid(row=3, column=2, sticky="nsew", padx=5)

    # populate the middle frame
    fasta_rbtn.grid(row=0, column=0)
    fastq_rbtn.grid(row=0, column=1)
    text_rbtn.grid(row=0, column=2)

    # populate the bottom frame
    maxsize_rbtn.grid(row=0, column=0, sticky="w")
    maxsize_entry.grid(row=0, column=1, sticky="we")
    split_n_rbtn.grid(row=1, column=0, sticky="w")
    split_n_entry.grid(row=1, column=1, sticky="we")
    seqid_rbtn.grid(row=2, column=0, sticky="w")
    seqid_pattern_entry.grid(row=2, column=1, sticky="we")
    sequence_rbtn.grid(row=3, column=0, sticky="w")
    sequence_pattern_entry.grid(row=3, column=1, sticky="we")

    # populate the main frame
    top_frame.grid(row=0, column=0, sticky="nsew")
    middle_frame.grid(row=1, column=0, sticky="nsw")
    bottom_frame.grid(row=2, column=0, sticky="nsew")
    pattern_hint_lbl.grid(row=3, column=0, sticky="w")

    banner_frame = ttk.Frame(root)
    ttk.Label(banner_frame, text="Fastsplit", font=tkfont.Font(size=20)).grid(row=0, column=0, sticky="w")
    ttk.Label(banner_frame, text="Split large sequences or text files into smaller files").grid(
        row=1, column=0, sticky="w"
    )

    banner_frame.grid(row=0, column=0, sticky="nsew")

    ttk.Separator(root, orient="horizontal").grid(row=1, column=0, sticky="nsew")

    mainframe.grid(row=2, column=0, sticky="nsew")

    # configure the resizing
    root.rowconfigure(2, weight=1)
    root.columnconfigure(0, weight=1)
    mainframe.columnconfigure(0, weight=1)
    top_frame.columnconfigure(0, weight=1)
    middle_frame.columnconfigure(2, weight=1)
    bottom_frame.columnconfigure(1, weight=1)

    root.mainloop()


argparser = argparse.ArgumentParser()

format_group = argparser.add_mutually_exclusive_group()
format_group.add_argument(
    "--fasta", dest="format", action="store_const", const="fasta", help="Input file is a fasta file"
)
format_group.add_argument(
    "--fastq", dest="format", action="store_const", const="fastq", help="Input file is a fastq file"
)
format_group.add_argument("--text", dest="format", action="store_const", const="text", help="Input file is a text file")

split_group = argparser.add_mutually_exclusive_group()
split_group.add_argument("--split_n", type=int, help="number of files to split into")
split_group.add_argument("--maxsize", type=parse_size, help="Maximum size of output file")
split_group.add_argument(
    "--seqid", metavar="PATTERN", help="split the records that match the sequence identifier pattern"
)
split_group.add_argument(
    "--sequence", metavar="PATTERN", help="split the records that match the sequence motif pattern"
)


argparser.add_argument("--compressed", action="store_true", help="Compress output files with gzip")
argparser.add_argument("infile", nargs="?", help="Input file name")
argparser.add_argument("outfile", nargs="?", help="outfile file template")


args = argparser.parse_args()

if not args.format:
    launch_gui()
else:
    try:
        with warnings.catch_warnings(record=True) as warns:
            fastsplit(
                args.format,
                args.split_n,
                args.maxsize,
                args.seqid,
                args.sequence,
                args.infile,
                args.compressed,
                args.outfile,
            )
            for w in warns:
                print(w.message)
    except ValueError as ex:
        sys.exit(ex)
