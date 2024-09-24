#!/usr/bin/env python3

import argparse
import ast
import gzip
import os
import sys
import tkinter as tk
import tkinter.filedialog as tkfiledialog
import tkinter.font as tkfont
import tkinter.messagebox
import warnings
from tkinter import ttk
from typing import Iterable, Iterator, Optional, Set, TextIO, Union, cast

from fastutils import (
    Pattern,
    ext_gz,
    fasta_iter,
    fastq_iter,
    parse_pattern_optional,
)

# extensions of the fasta files
fasta_exts = {".fas", ".fasta"}
# extensions of the fastq files
fastq_exts = {".fq", ".fastq"}


def fastmerge(
    file_list: Iterable[str], file_types: Optional[Set[str]], seqid_pattern: str, sequence_pattern: str, output: TextIO
) -> None:
    """
    Main merging function
    """
    if not file_types:
        fastmerge_pure(file_list, output)
    else:
        if seqid_pattern or sequence_pattern:
            if ".fas" in file_types:
                fastmerge_fasta_filter(
                    file_list, parse_pattern_optional(seqid_pattern), parse_pattern_optional(sequence_pattern), output
                )
            else:
                fastmerge_fastq_filter(
                    file_list, parse_pattern_optional(seqid_pattern), parse_pattern_optional(sequence_pattern), output
                )
        else:
            fastmerge_type(file_list, file_types, output)


def list_files(file_list: Iterable[str]) -> Iterator[Union[str, os.DirEntry]]:
    """
    For each file in 'file_list' yield its name.
    For each directory, yields the DirEnty of file inside it
    """
    for filename in file_list:
        filename = filename.strip()
        if os.path.isdir(filename):
            for entry in filter(os.DirEntry.is_file, os.scandir(filename)):
                yield entry
        elif os.path.exists(filename):
            yield filename


def fastmerge_pure(file_list: Iterable[str], output: TextIO) -> None:
    """
    Merge the files, extracting all gzip archives
    """
    for entry in list_files(file_list):
        # open the file as archive or text file
        if os.path.splitext(entry)[1] == ".gz":
            file = cast(TextIO, gzip.open(entry, mode="rt", errors="replace"))
        else:
            file = open(entry, errors="replace")
        # copy the lines to the output
        with file:
            for line in file:
                print(line.rstrip(), file=output)


def fastmerge_type(file_list: Iterable[str], file_types: Set[str], output: TextIO) -> None:
    """
    Merge the file only of the given 'file_types', extracting all gzip archives
    """
    for entry in list_files(file_list):
        # skip the files of the wrong type
        if ext_gz(entry) not in file_types:
            continue
        # open the file as archive or text file
        if os.path.splitext(entry)[1] == ".gz":
            file = cast(TextIO, gzip.open(entry, mode="rt", errors="replace"))
        else:
            file = open(entry, errors="replace")
        # copy the lines to the output
        with file:
            for line in file:
                print(line.rstrip(), file=output)


def fastmerge_fasta_filter(
    file_list: Iterable[str], seqid_pattern: Optional[Pattern], sequence_pattern: Optional[Pattern], output: TextIO
) -> None:
    """
    Merge the fasta files, extraction all gzip archives.
    Filter records with the given patterns
    """
    for entry in list_files(file_list):
        # skip the files of the wrong type
        if ext_gz(entry) not in fasta_exts:
            continue
        # copy the lines to the output
        if os.path.splitext(entry)[1] == ".gz":
            file = cast(TextIO, gzip.open(entry, mode="rt", errors="replace"))
        else:
            file = open(entry, errors="replace")
        with file:
            # warn about the line breaks
            line_breaks_warned = False
            for seqid, sequence in fasta_iter(file):
                if not line_breaks_warned and sequence_pattern and len(sequence) > 1:
                    line_breaks_warned = True
                    warnings.warn(
                        f"The file {file.name} contains sequences interrupted with line breaks, and the search for sequence motifs will not work reliably in this case - some sequences with the specified motif will likely be missed. Please first transform your file into a fasta file without line breaks interrupting the sequences."
                    )
                # skip sequences that don't match the seqid pattern
                if seqid_pattern:
                    if not seqid_pattern.match(seqid):
                        continue
                # skip sequences that don't match the sequence pattern
                if sequence_pattern:
                    if not any(map(sequence_pattern.match, sequence)):
                        continue
                # copy the lines into the output
                print(seqid.rstrip(), file=output)
                for chunk in sequence:
                    print(chunk.rstrip(), file=output)


def fastmerge_fastq_filter(
    file_list: Iterable[str], seqid_pattern: Optional[Pattern], sequence_pattern: Optional[Pattern], output: TextIO
) -> None:
    """
    Merge the fastq files, extraction all gzip archives.
    Filter records with the given patterns
    """
    for entry in list_files(file_list):
        # skip the files of the wrong type
        if ext_gz(entry) not in fastq_exts:
            continue
        # copy the lines to the output
        if os.path.splitext(entry)[1] == ".gz":
            file = cast(TextIO, gzip.open(entry, mode="rt", errors="replace"))
        else:
            file = open(entry, errors="replace")
        with file:
            for seqid, sequence, quality_score_seqid, quality_score in fastq_iter(file):
                # skip sequences that don't match the seqid pattern
                if seqid_pattern:
                    if not seqid_pattern.match(seqid):
                        continue
                # skip sequences that don't match the sequence pattern
                if sequence_pattern:
                    if not sequence_pattern.match(sequence):
                        continue
                print(seqid.rstrip(), file=output)
                print(sequence.rstrip(), file=output)
                print(quality_score_seqid.rstrip(), file=output)
                print(quality_score.rstrip(), file=output)


def launch_gui() -> None:
    """
    Main function for the GUI
    """
    # initializing the gui
    root = tk.Tk()
    root.title("Fastmerge")
    root.rowconfigure(2, weight=1)
    if os.name == "nt":
        root.wm_iconbitmap(os.path.join("data", "Fastmerge_icon.ico"))
    mainframe = ttk.Frame(root, padding=5)
    mainframe.grid(column=0, row=2, sticky="nsew")

    style = ttk.Style()
    style.configure("MergeButton.TButton", background="blue")

    # banner frame
    banner_frame = ttk.Frame(root)
    banner_frame.columnconfigure(1, weight=1)
    banner_img = tk.PhotoImage(file=os.path.join("data", "iTaxoTools Digital linneaeus MICROLOGO.png"))
    banner_image = ttk.Label(banner_frame, image=banner_img)
    banner_image.grid(row=0, column=3, rowspan=3, sticky="nse")
    program_name = ttk.Label(banner_frame, text="Fastmerge", font=tkfont.Font(size=20))
    program_name.grid(row=1, column=0, sticky="sw")
    program_description = ttk.Label(
        banner_frame, text="Merge multiple sequences or text files into a single large file"
    )
    program_description.grid(row=2, column=0, sticky="sw")
    banner_frame.grid(column=0, row=0, sticky="nsew")

    ttk.Separator(root, orient="horizontal").grid(column=0, row=1, sticky="we")

    # frames for different parts
    top_frame = ttk.Frame(mainframe)
    middle_frame = ttk.Frame(mainframe)
    bottom_frame = ttk.Frame(mainframe)

    # list of files and directories
    file_list_lbl = ttk.Label(top_frame, text="List of input files and directories")
    file_list_var = tk.StringVar()
    file_list_box = tk.Listbox(top_frame, listvariable=file_list_var, height=10)
    file_scroll = ttk.Scrollbar(top_frame, orient=tk.VERTICAL, command=file_list_box.yview)
    file_list_box.configure(yscrollcommand=file_scroll.set)

    # browse files button command
    def browse_files() -> None:
        newpaths = list(tkfiledialog.askopenfilenames())
        if newpaths:
            for i, newpath in enumerate(newpaths):
                try:
                    newpaths[i] = os.path.relpath(newpath)
                except Exception:
                    newpaths[i] = os.path.abspath(newpath)
            file_list_box.insert("end", *newpaths)

    # browse directory button command
    def browse_directory() -> None:
        newpath: Optional[str] = tkfiledialog.askdirectory()
        if newpath:
            try:
                newpath = os.path.relpath(newpath)
            except Exception:
                newpath = os.path.abspath(newpath)
            file_list_box.insert("end", newpath)

    # remove file button command
    def remove_file() -> None:
        for idx in file_list_box.curselection():
            file_list_box.delete(idx)

    # clear files button command
    def clear_files() -> None:
        file_list_box.delete(0, "end")

    # buttons for the list of files
    browse_files_button = ttk.Button(top_frame, text="Browse files", command=browse_files)
    browse_directory_button = ttk.Button(top_frame, text="Browse a directory", command=browse_directory)
    remove_file_button = ttk.Button(top_frame, text="Remove", command=remove_file)
    clear_files_button = ttk.Button(top_frame, text="Clear", command=clear_files)

    # place the file selection widget group
    file_list_lbl.grid(row=0, column=0)
    file_list_box.grid(row=1, rowspan=5, column=0, sticky="nswe")
    file_scroll.grid(row=1, rowspan=5, column=1, sticky="nsw")
    browse_files_button.grid(row=1, column=2, sticky="nwe")
    browse_directory_button.grid(row=2, column=2, sticky="nwe")
    remove_file_button.grid(row=3, column=2, sticky="nwe")
    clear_files_button.grid(row=4, column=2, sticky="nwe")

    # radiobuttons for the format selection
    format_var = tk.StringVar()
    r_any = ttk.Radiobutton(middle_frame, text="All files", variable=format_var, value="")
    r_fasta = ttk.Radiobutton(middle_frame, text="fasta", variable=format_var, value="fasta")
    r_fastq = ttk.Radiobutton(middle_frame, text="fastq", variable=format_var, value="fastq")

    # pattern entry widgets
    seqid_pattern = tk.StringVar()
    seqid_pattern_lbl = ttk.Label(bottom_frame, text="Sequence identifier pattern¹", state=tk.DISABLED)
    seqid_pattern_entry = ttk.Entry(bottom_frame, textvariable=seqid_pattern, state=tk.DISABLED)
    sequence_pattern = tk.StringVar()
    sequence_pattern_lbl = ttk.Label(bottom_frame, text="Sequence motif pattern¹", state=tk.DISABLED)
    sequence_pattern_entry = ttk.Entry(bottom_frame, textvariable=sequence_pattern, state=tk.DISABLED)
    pattern_hint_lbl = ttk.Label(mainframe, text="\t¹The search words should be in double quotes", state=tk.DISABLED)
    # they are initially disabled

    # methods to enable and disable the patterns
    def enable_patterns() -> None:
        seqid_pattern_lbl.configure(state="normal")
        seqid_pattern_entry.configure(state="normal")
        sequence_pattern_lbl.configure(state="normal")
        sequence_pattern_entry.configure(state="normal")
        pattern_hint_lbl.configure(state="normal")

    def disable_patterns() -> None:
        seqid_pattern_lbl.configure(state="disabled")
        seqid_pattern_entry.configure(state="disabled")
        sequence_pattern_lbl.configure(state="disabled")
        sequence_pattern_entry.configure(state="disabled")
        pattern_hint_lbl.configure(state="disabled")

    # configure enabling and disabling of patterns
    r_any.configure(command=disable_patterns)
    r_fasta.configure(command=enable_patterns)
    r_fastq.configure(command=enable_patterns)

    # place the radiobuttons
    r_any.grid(row=0, column=0)
    r_fasta.grid(row=0, column=1)
    r_fastq.grid(row=0, column=2)

    # place the pattern entries
    seqid_pattern_lbl.grid(row=0, column=0)
    seqid_pattern_entry.grid(row=0, column=1, sticky="nsew")
    sequence_pattern_lbl.grid(row=1, column=0)
    sequence_pattern_entry.grid(row=1, column=1, sticky="nsew")
    pattern_hint_lbl.grid(row=3, column=0, sticky="w")

    # output file entry
    output_file_lbl = ttk.Label(top_frame, text="Output file")
    output_file = tk.StringVar()
    output_file_entry = ttk.Entry(top_frame, textvariable=output_file)

    # compress output checkbox
    compress_output = tk.BooleanVar()
    compress_output_chk = ttk.Checkbutton(top_frame, text="Compress output", variable=compress_output)

    # command for the merge button
    def gui_merge() -> None:
        if not file_list_var.get():
            tkinter.messagebox.showwarning("Warning", "No input files given")
            return
        if not output_file.get():
            tkinter.messagebox.showwarning("Warning", "No output file given")
            return
        file_list = cast(tuple[str], ast.literal_eval(file_list_var.get()))
        file_types = None
        if format_var.get() == "fasta":
            file_types = fasta_exts
        elif format_var.get() == "fastq":
            file_types = fastq_exts
        if compress_output.get():
            output = cast(TextIO, gzip.open(output_file.get() + ".gz", mode="wt", errors="replace"))
        else:
            output = open(output_file.get(), mode="w", errors="replace")

        try:
            # catch all warnings
            with warnings.catch_warnings(record=True) as warns:
                fastmerge(file_list, file_types, seqid_pattern_entry.get(), sequence_pattern_entry.get(), output)
            # display the warnings generated during the conversion
            for w in warns:
                tkinter.messagebox.showwarning("Warning", str(w.message))
            # notify the user that the converions is finished
            tkinter.messagebox.showinfo("Done.", "The merging has been completed")
        # show the ValueErrors and FileNotFoundErrors
        except ValueError as ex:
            tkinter.messagebox.showerror("Error", str(ex))
        except FileNotFoundError as ex:
            tkinter.messagebox.showerror("Error", str(ex))

    # command for the output browse button

    def output_browse() -> None:
        newpath: Optional[str] = tkfiledialog.asksaveasfilename()
        if newpath:
            try:
                newpath = os.path.relpath(newpath)
            except Exception:
                newpath = os.path.abspath(newpath)
            output_file.set(newpath)

    # the output browse button
    browse_output = ttk.Button(top_frame, text="Browse output file", command=output_browse)

    # place the output group
    output_file_lbl.grid(row=0, column=4)
    output_file_entry.grid(row=1, column=4)
    browse_output.grid(row=1, column=5)
    compress_output_chk.grid(row=2, column=4)

    # the merge button
    merge_btn = ttk.Button(top_frame, text="Merge", command=gui_merge, style="MergeButton.TButton")

    # place the merge button
    merge_btn.grid(row=5, column=0, columnspan=6)

    # some spacing between input and output widget in the top_frame
    ttk.Label(top_frame).grid(row=0, column=3, padx=20)

    # place the frames
    top_frame.grid(row=0, column=0, sticky="nsew")
    middle_frame.grid(row=1, column=0, sticky="nsew")
    bottom_frame.grid(row=2, column=0, sticky="nsew")

    # configure the resizing
    root.rowconfigure(0, weight=1)
    root.columnconfigure(0, weight=1)
    mainframe.rowconfigure(0, weight=1)
    mainframe.columnconfigure(0, weight=1)
    top_frame.rowconfigure(4, weight=1)
    top_frame.columnconfigure(3, weight=1)
    middle_frame.columnconfigure(3, weight=1)
    bottom_frame.columnconfigure(1, weight=1)

    root.mainloop()


argparser = argparse.ArgumentParser()
argparser.add_argument("--cmd", action="store_true", help="Launches in the command-line mode")
format_group = argparser.add_mutually_exclusive_group()
format_group.add_argument(
    "--fasta", dest="ext", action="store_const", const=fasta_exts, help="Process only .fas and .fas.gz files"
)
format_group.add_argument(
    "--fastq",
    dest="ext",
    action="store_const",
    const=fastq_exts,
    help="Process only .fq, .fq.gz, .fastq and .fastq.gz files",
)
argparser.add_argument("--seqid", metavar="PATTERN", help="Filter pattern for sequence names")
argparser.add_argument("--sequence", metavar="PATTERN", help="Filter pattern for sequences")

args = argparser.parse_args()

if not args.cmd:
    launch_gui()
else:
    try:
        with warnings.catch_warnings(record=True) as warns:
            fastmerge(sys.stdin, args.ext, args.seqid, args.sequence, sys.stdout)
            for w in warns:
                print(w.message)
    except ValueError as ex:
        sys.exit(ex)
