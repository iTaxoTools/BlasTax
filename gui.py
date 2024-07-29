#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os
import tkinter.filedialog
import tkinter.simpledialog
from pathlib import Path
from tkinter import (
    END,
    Button,
    Checkbutton,
    Entry,
    IntVar,
    Label,
    LabelFrame,
    StringVar,
    Tk,
    Toplevel,
    filedialog,
)
from tkinter.font import Font
from tkinter.messagebox import showinfo
from tkinter.ttk import Combobox, Style

from PIL import Image, ImageTk

from core import (
    blastn_parse,
    blastx_parse,
    make_database,
    museoscript_original_reads,
    museoscript_parse,
    run_blast,
    run_blast_align,
)
from utils import check_fasta_headers, remove_gaps


def get_blast_env() -> dict:
    here = Path(__file__).parent
    bin = here / "bin"
    env = os.environ.copy()
    env["PATH"] += f"{os.pathsep}{bin}"
    return env


BLAST_ENV = get_blast_env()


def get_itaxotools_logo() -> str:
    here = Path(__file__).parent
    logo = "iTaxoTools Digital linneaeus MICROLOGO.png"
    path = Path(here / logo)
    return str(path)


LOGO = get_itaxotools_logo()


def start_processing():
    if run_blast_var.get() == 1:
        star()
    elif run_batch_var.get() == 1:
        loop_blast()
    elif build_db_var.get() == 1:
        make_db_button_cmd()

    else:
        showinfo(title="warning", message="Please select a checkbox")


def make_db_button_cmd():
    if fndb == "":
        print("Input: ", fndb)
        return showinfo(
            title="warning", message="The build database file is not selected!"
        )
    if (
        database_type.get() != "Nucleic acid sequence"
        and database_type.get() != "Protein sequence"
    ):
        return showinfo(title="warning", message="The database type is not selected!")
    if database_name.get() == "":
        return showinfo(title="warning", message="Database name is not set!")

    header_check_result = check_fasta_headers(fndb)
    if header_check_result == "length":
        return showinfo(
            title="warning",
            message="One or more sequence headers in the FASTA file exceed 51 characters! Please check and edit headers!",
        )
    elif header_check_result == "special":
        return showinfo(
            title="warning",
            message="One or more sequence headers in the FASTA file contain special characters! Please check and edit headers!",
        )

    if database_type.get() == "Nucleic acid sequence":
        t = "nucl"
    if database_type.get() == "Protein sequence":
        t = "prot"

    # Extract directory path from fndb
    directory_path = os.path.dirname(fndb)
    # Define the output filename
    output_filename_db = os.path.join(directory_path, database_name.get())

    n = database_name.get()

    if make_database(fndb, output_filename_db, t, n):
        showinfo(title="info", message="Database built successfully!")
    else:
        showinfo(title="info", message="Database creation failed!")


### MAKE an Instruction depending on what checkbox is clicked

##### NEW CODE #####


### CREATE A NEW OUTPUT FILE FOR THE REGULAR BLAST ###
def get_new_filename():
    new_filename = filedialog.asksaveasfilename(
        defaultextension=".out", filetypes=[("Text files", "*.txt")]
    )
    return new_filename


### BROWSE FILES ###
def select_fadb_button_cmd(type, number):
    global fndb
    global db
    global outp
    global extnucl
    if type == "query":
        fndb = tkinter.filedialog.askopenfilename()
        if number == 1:
            select_query.delete(0, tkinter.END)
            select_query.insert(tkinter.END, fndb)
        elif number == 2:
            select_query2.delete(0, tkinter.END)
            select_query2.insert(tkinter.END, fndb)
        elif number == 3:
            select_query3.delete(0, tkinter.END)
            select_query3.insert(tkinter.END, fndb)
    elif type == "database":
        db = tkinter.filedialog.askopenfilename()
        if number == 1:
            select_db.delete(0, tkinter.END)
            select_db.insert(tkinter.END, db)
        if number == 2:
            select_db2.delete(0, tkinter.END)
            select_db2.insert(tkinter.END, db)

    elif type == "output":
        if number == 1:
            outp = get_new_filename()
            select_out.delete(0, tkinter.END)
            select_out.insert(tkinter.END, outp)
        elif number == 3:
            outp = tkinter.filedialog.askopenfilename()
            # select_out3.delete(0, tkinter.END)
            # select_out3.insert(tkinter.END, outp)
    elif type == "extra_nucleotide_file":
        extnucl = tkinter.filedialog.askopenfilename()
        extra_nucleotide_entry.delete(0, tkinter.END)
        extra_nucleotide_entry.insert(tkinter.END, extnucl)


def select_directory(type):
    global seldir
    global outdir
    if type == "query":
        seldir = tkinter.filedialog.askdirectory()
        select_query2.delete(0, tkinter.END)
        select_query2.insert(tkinter.END, seldir)
    elif type == "output":
        outdir = tkinter.filedialog.askdirectory()
        select_out2.delete(0, tkinter.END)
        select_out2.insert(tkinter.END, outdir)


##################################


### EXTRA NUCLEOTIDE FILE WIDGETS FOR LOOP-BLASTX ###
def switch_nucleotide_widgets(state):
    if blast_typeVar2.get() == "blastx":
        # Make the widgets for extra nucleotide file active
        extra_nucleotide_entry.grid(row=3, column=2, sticky="we", pady=(10, 0))
        extra_nucleotide_browse_button.grid(
            row=3, column=3, sticky="we", padx=(5, 25), pady=(10, 0)
        )
    else:
        # Remove or hide the widgets for extra nucleotide file
        extra_nucleotide_entry.grid_forget()
        extra_nucleotide_browse_button.grid_forget()


### EXTRA WIDGETS if museoscript mode was chosen
def museoscript_widgets():
    if museoscript_mode_var.get():
        # Make the widgets for museoscript output file
        museoscript_parameters.grid(
            row=6, column=0, columnspan=2, sticky="w", pady=(10, 0), padx=(10, 5)
        )
        similarity_threshold_label.grid(
            row=8, column=0, sticky="e", pady=(10, 0), padx=(10, 5)
        )
        similarity_threshold_entry.grid(
            row=8, column=1, sticky="w", pady=(10, 0), padx=(0, 25)
        )
        museo_script_output_text.grid(
            row=8, column=2, columnspan=2, sticky="e", pady=(10, 0), padx=(25, 5)
        )
        museo_script_output.grid(row=8, column=4, sticky="w", pady=(10, 0), padx=(0, 5))

        # Set values for Outfmt and Other cmd, and make them read-only
        outfmt.config(state="normal")  # Temporarily enable to set value
        outfmt.delete(0, "end")
        outfmt.insert(0, "6")
        outfmt.config(state="readonly")  # Make read-only

        other.config(state="normal")  # Temporarily enable to set value
        other.delete(0, "end")
        other.insert(0, "qseqid sseqid sacc stitle pident qseq")
        other.config(state="readonly")  # Make read-only

        # Freeze the combobox to "blastn"
        blast_typeVar.set("blastn")
        blast_type.config(state="disabled")

        # Show the new checkbox for retrieving original reads
        extra_museoscript_checkbox.grid(
            row=7, column=0, columnspan=2, sticky="e", padx=(0, 0), pady=1
        )

    else:
        # Remove or hide the widgets for museoscript output file
        museoscript_parameters.grid_forget()
        similarity_threshold_label.grid_forget()
        similarity_threshold_entry.grid_forget()
        museo_script_output_text.grid_forget()
        museo_script_output.grid_forget()

        # Re-enable the combobox
        blast_type.config(state="readonly")

        # Make Outfmt and Other cmd editable
        outfmt.config(state="normal")
        other.config(state="normal")

        # Hide the new checkbox for retrieving original reads
        extra_museoscript_checkbox.grid_forget()


### MUSEOSCRIPT MODIFICATION WITH ORIGINAL READS RETRIEVE
# blast process
def star(type=None, query=None):
    # Redirect output to the output folder
    filebase = os.path.dirname(str(select_query.get()))
    output_file_blast = os.path.join(filebase, select_out.get())

    print("blast type; ", blast_type.get())
    print("query: ", str(select_query.get()))
    print("outfmt: ", outfmt.get())
    print("evalue: ", evalue.get())
    print("db: ", str(select_db.get()))
    print("Threads: ", threads.get())
    print("Other cmd", other.get())
    db = str(select_db.get().rsplit(".", 1)[0])

    # remove gaps
    input_file = str(select_query.get())
    file_name, file_extension = input_file.rsplit(".", 1)
    temporary_file = file_name + "_tmp." + file_extension
    remove_gaps(input_file, temporary_file)

    if not run_blast(
        blast_binary=blast_type.get(),
        query_path=temporary_file,
        database_path=db,
        output_path=output_file_blast,
        evalue=evalue.get(),
        num_threads=threads.get(),
        outfmt=outfmt.get(),
        other=other.get(),
    ):
        showinfo(
            title="warning",
            message="Wrong alignment!\nPlease make sure the parameters are set correctly!",
        )

    if museoscript_mode_var.get() == 1:  # museoscript checkbox selected
        museo_filename = str(museo_script_output.get())
        museo_filename = os.path.join(filebase, museo_filename)
        if extra_museoscript_mode_var.get() == 1:
            museoscript_original_reads(
                blast_path=output_file_blast,
                original_query_path=temporary_file,
                output_path=museo_filename,
                pident_threshold=float(similarity_threshold_entry.get()),
            )
        else:
            museoscript_parse(
                blast_path=output_file_blast,
                output_path=museo_filename,
                pident_threshold=float(similarity_threshold_entry.get()),
            )


def blast_align(input_file):
    # Redirect output to the output folder
    filebase = os.path.basename(input_file)
    output_file = filebase.split(".")[0] + ".out"
    output_file = os.path.join(select_out2.get(), output_file)
    print("db: ", select_db2.get())
    print("input file: ", input_file)
    # remove gaps and store new sequences into temporary file
    base, ext = os.path.splitext(input_file)
    temporary_file = base + "_temp" + ext
    remove_gaps(input_file, temporary_file)
    # remove .ext from the db name
    db = str(select_db2.get().rsplit(".", 1)[0])

    if run_blast_align(
        blast_binary=blast_type2.get(),
        query_path=temporary_file,
        database_path=db,
        output_path=output_file,
        evalue=evalue2.get(),
        num_threads=int(threads2.get()),
    ):
        print("BLAST execution successful.")
        # Print the content of the output file
        with open(output_file, "r") as f:
            print("Content of the output file:")
            print(f.read())
    else:
        showinfo(
            title="warning",
            message="Wrong alignment!\nPlease make sure the parameters are set correctly!",
        )

    os.remove(temporary_file)

    filesplit = filebase.split(".")
    modified_output = (
        str(select_out2.get())
        + "/"
        + filesplit[0]
        + "_blastmatchesadded."
        + filesplit[1]
    )
    print("output file: ", output_file)
    if blast_type2.get() == "blastx":
        db_name = select_db2.get()
        db_name = db_name.split("/")[-1]
        db_name = db_name.rsplit(".", 1)[0]
        blastx_parse(
            input_path=input_file,
            blast_result_path=output_file,
            output_path=modified_output,
            extra_nucleotide_path=extra_nucleotide_entry.get(),
            database_name=db_name,
        )
    elif blast_type2.get() == "blastn":
        db_name = select_db2.get()
        db_name = db_name.rsplit("/", 1)[-1]
        blastn_parse(
            input_path=input_file,
            blast_result_path=output_file,
            output_path=modified_output,
            database_name=db_name,
        )


def loop_blast():
    if os.path.isfile(select_query2.get()):
        # single file
        file = select_query2.get()
        blast_align(file)
    else:
        # run in a loop
        directory = str(select_query2.get())
        if not os.path.exists(directory):
            os.makedirs(directory)
        for file in os.listdir(directory):
            if file.endswith((".fa", ".fas", ".fasta")):
                blast_align(file)


def select_fa_button_Cmd():
    global fnfa
    fnfa = tkinter.filedialog.askopenfilename()
    query_sequence.delete(0, END)
    if fnfa != "":
        #        fa_input.insert(END, "The files you selected:" + fnfa)
        select_query.insert(END, "The files you selected:" + fnfa)
    else:
        select_query.insert(END, "Enter a sequence here or select a sequence file:")
    #        fa_input.insert(END, "Enter a sequence here or select a sequence file:")
    pass


### INSTRUCTIONS FOR A HELP BUTTON ###
def main_instructions():
    top = Toplevel()

    top.title("Instruction")
    Label(
        top,
        text="Instructions:\n\n1. Please click the [Build database] button to set up the database for the first time\n \
    \n2.Input the sequence to be aligned into the text box or select the sequence file through the [Select file] button \
     \n\n3.Select the database to be compared and the comparison method.\n\n4.Set the e-value Value, output format and number of threads.The default e-value =1e-5, and the default output format is 0 and the default of threads is 4\n \
     \n5.(Optional) Any other command of BLAST like: -max_target_seqs 20 \n\n6.Click [Start] button for comparison, and the comparison results will be displayed here and saved in result.txt\n\n7.Alignment time depends on sequence size and computer performance \
     \n",
    ).pack()
    Button(top, text="Close help message", command=top.destroy).pack()


### Checkbox control functions
def on_checkbox_click(frame, checkbox, all_frames):
    state = checkbox.var.get()
    for other_frame in all_frames:
        if other_frame != frame:
            for widget in other_frame.winfo_children():
                widget.configure(state="disable" if state == 1 else "normal")
    if checkbox == museoscript_checkbox:
        if state == 1:
            blast_typeVar.set("blastn")
            blast_type.config(state="disabled")
        else:
            blast_type.config(state="readonly")

        # Freeze the outfmt and other command when museoscript mode is selected


def create_checkbox(frame, text, row, column, variable, all_frames):
    checkbox = Checkbutton(
        frame, text=text, bg="#fffacd", onvalue=1, offvalue=0, variable=variable
    )
    checkbox.grid(row=row, column=column, columnspan=6, sticky="w", padx=(6, 0), pady=1)
    checkbox.var = variable
    checkbox.configure(command=lambda: on_checkbox_click(frame, checkbox, all_frames))
    return checkbox


###GUI part of the program ###

top = Tk()
top.title("BLAST-Align")
top.geometry("960x560")

top.rowconfigure(1, weight=1)
top.rowconfigure(2, weight=1)
top.rowconfigure(3, weight=1)
top.rowconfigure(4, weight=1)
top.columnconfigure(0, weight=1)

style = Style()
fnfa = ""
fndb = ""

### CREATE MAIN FRAMES ###
banner_frame = LabelFrame(top, bg="#f0f0f0")

second_frame = LabelFrame(top, bg="#fffacd")
second_frame.grid(column=0, row=1, sticky="nsew")
second_frame.columnconfigure(1, weight=1)
second_frame.columnconfigure(2, weight=1)
second_frame.columnconfigure(0, weight=1)
second_frame.columnconfigure(3, weight=1)
second_frame.columnconfigure(4, weight=1)
second_frame.columnconfigure(5, weight=1)
second_frame.rowconfigure(0, weight=1)
second_frame.rowconfigure(1, weight=1)
second_frame.rowconfigure(2, weight=1)

third_frame = LabelFrame(top, bg="#fffacd")
third_frame.grid(column=0, row=2, sticky="nsew")
third_frame.columnconfigure(0, weight=1)
third_frame.columnconfigure(1, weight=1)
third_frame.columnconfigure(2, weight=1)
third_frame.columnconfigure(3, weight=1)
third_frame.columnconfigure(4, weight=1)
third_frame.columnconfigure(5, weight=1)
third_frame.rowconfigure(0, weight=1)
third_frame.rowconfigure(1, weight=1)
third_frame.rowconfigure(2, weight=1)
third_frame.rowconfigure(3, weight=1)
third_frame.rowconfigure(4, weight=1)

fourth_frame = LabelFrame(top, bg="#fffacd")
fourth_frame.grid(column=0, row=3, sticky="nsew")
fourth_frame.columnconfigure(0, weight=1)
fourth_frame.columnconfigure(1, weight=1)
fourth_frame.columnconfigure(2, weight=1)
fourth_frame.columnconfigure(3, weight=1)
fourth_frame.columnconfigure(4, weight=1)
fourth_frame.columnconfigure(5, weight=1)

fifth_frame = LabelFrame(top, bg="#fffacd")
fifth_frame.grid(column=0, row=4, sticky="nsew")
fifth_frame.columnconfigure(0, weight=1)
fifth_frame.columnconfigure(4, weight=1)


### CHECKBOXES ###
main_frames = [second_frame, third_frame, fourth_frame]
run_blast_var = IntVar()
run_blast_checkbox = create_checkbox(
    second_frame, "Run regular BLAST", 0, 0, run_blast_var, main_frames
)

run_batch_var = IntVar()
run_batch_checkbox = create_checkbox(
    third_frame, "Run BLAST-Align", 0, 0, run_batch_var, main_frames
)

build_db_var = IntVar()
run_batch_checkbox3 = create_checkbox(
    fourth_frame, "Build BLAST database", 0, 0, build_db_var, main_frames
)


### Title Frame ###
banner_frame = LabelFrame(top, bg="#f0f0f0")
banner_img = ImageTk.PhotoImage(Image.open(LOGO))

my_image_label = Label(banner_frame, image=banner_img).grid(
    row=0, column=0, rowspan=3, sticky="nsew"
)
banner_frame.grid(column=0, row=0, sticky="nsew")

program_name = Label(banner_frame, text="BLAST-Align", bg="#f0f0f0", font=Font(size=20))
program_name.grid(row=1, column=1)
program_description = Label(
    banner_frame,
    text="Add sequences to alignment if matching in Blast search",
    bg="#f0f0f0",
)
program_description.grid(row=1, column=2, sticky="nsew", ipady=4, ipadx=15)

author = Label(
    banner_frame,
    text="Code by Nikita Kulikov, Anja-Kristina Schulz and Stefanos Patmanidis \nGUI modified from BLAST-GUI by Du et al. (2020) / https://github.com/byemaxx/BlastGUI",
    font=Font(size=8),
    bg="#f0f0f0",
    anchor="w",
    justify="left",
)
author.grid(row=2, column=1, columnspan=2)


###### SECOND FRAME ######

# Texts
query = Label(second_frame, text="Select query files", bg="#fffacd")
query.grid(row=1, column=0, columnspan=2, sticky="w", padx=10, pady=1)
database = Label(second_frame, text="Select database", bg="#fffacd")
database.grid(row=1, column=2, columnspan=2, sticky="w", padx=25, pady=1)
output = Label(second_frame, text="Select output file", bg="#fffacd")
output.grid(row=1, column=4, columnspan=2, sticky="w", padx=25, pady=1)
# Select query files and button
select_query = StringVar()
select_query = Entry(second_frame, width=25, textvariable=select_query)
select_query.grid(row=2, column=0, sticky="we", padx=(10, 5))

button1 = Button(
    second_frame,
    text="Browse",
    width=8,
    height=2,
    command=lambda: select_fadb_button_cmd("query", 1),
)
button1.grid(row=2, column=1, sticky="we", padx=(5, 25))

# Select database and button

select_db = StringVar()
select_db = Entry(second_frame, width=25, textvariable=select_db)
select_db.grid(row=2, column=2, sticky="we", padx=(25, 5))

button2 = Button(
    second_frame,
    text="Browse",
    width=8,
    height=2,
    command=lambda: select_fadb_button_cmd("database", 1),
)
button2.grid(row=2, column=3, sticky="we", padx=(5, 25))

# Select output file and button
select_out = StringVar()
select_out = Entry(second_frame, width=25, textvariable=select_out)
select_out.grid(row=2, column=4, sticky="we", padx=(25, 5))

button3 = Button(
    second_frame,
    text="Browse",
    width=8,
    height=2,
    command=lambda: select_fadb_button_cmd("output", 1),
)
button3.grid(row=2, column=5, sticky="we", padx=(5, 10))

# Text
# New label in the next row
third_row = Label(second_frame, text="Or paste query sequence here:", bg="#fffacd")
third_row.grid(row=3, column=0, columnspan=6, sticky="w", padx=10)

### next row

# New row with input fields and labels
query_sequence = Entry(
    second_frame,
    width=25,
    font=16,
)
query_sequence.grid(
    row=4, column=0, columnspan=2, sticky="we", padx=(10, 10), pady=(10, 0)
)

evalue = Label(second_frame, text="E-value:", bg="#fffacd")
evalue.grid(row=4, column=2, sticky="e", padx=(10, 0), pady=(10, 0))

evalue = Entry(second_frame, width=25)
evalue.insert(0, "1e-5")  # Default value
evalue.grid(row=4, column=3, sticky="we", padx=(0, 5), pady=(10, 0))

threads = Label(second_frame, text="Threads:", bg="#fffacd")
threads.grid(row=4, column=4, sticky="e", padx=(10, 0), pady=(10, 0))

threads = Entry(second_frame, width=25)
threads.insert(0, "4")  # Default value
threads.grid(row=4, column=5, sticky="we", padx=(0, 10), pady=(10, 0))

# next row
outfmt = Label(second_frame, text="Outfmt:", bg="#fffacd")
outfmt.grid(row=5, column=0, sticky="e", padx=(10, 0), pady=(10, 0))

outfmt = Entry(second_frame, width=25)
outfmt.insert(0, "0")  # Default value
outfmt.grid(row=5, column=1, sticky="we", padx=(0, 5), pady=(10, 0))

other = Label(second_frame, text="Other cmd:", bg="#fffacd")
other.grid(row=5, column=2, sticky="e", padx=(10, 0), pady=(10, 0))

other = Entry(second_frame, width=25)
other.grid(row=5, column=3, sticky="we", pady=(10, 0))

# Last row

method = Label(second_frame, text="Methods:", bg="#fffacd")
method.grid(row=5, column=4, sticky="e")

blast_typeList = [
    "blastn",
    "blastp",
    "blastx",
    "tblastn",
    "tblastx",
]
blast_typeVar = StringVar(value="blastn")
blast_type = Combobox(
    second_frame, textvariable=blast_typeVar, values=blast_typeList
)  # , font=('', 13))
blast_type.grid(row=5, column=5, padx=(0, 10), sticky="w")

###############################
### NEW checkbox for museoscript mode
museoscript_mode_var = IntVar()
museoscript_checkbox = create_checkbox(
    second_frame, "Museoscript mode", 0, 1, museoscript_mode_var, main_frames
)
museoscript_checkbox.configure(command=museoscript_widgets)

### NEW  WIDGET FOR MUSEOSCRIPT MODE ### PLACED HERE BECAUSE BLAST TYPE MUST BE DEFINED
museoscript_parameters = Label(
    second_frame, text="MUSEOSCRIPT PARAMETERS", bg="#fffacd"
)
museoscript_parameters.grid_forget()

museo_script_output_text = Label(
    second_frame, text="Museoscript output filename:", bg="#fffacd"
)
museo_script_output_text.grid_forget()
museo_script_output = Entry(second_frame, width=40)
# museo_script_output.insert(0, "Entry the name of museoscript output file")

similarity_threshold_label = Label(second_frame, text="Pident:", bg="#fffacd")
similarity_threshold_label.grid_forget()

similarity_threshold_entry = Entry(second_frame, width=25)
similarity_threshold_entry.insert(0, "0.9")
similarity_threshold_entry.grid_forget()

# EXTRA CHECKBOX FOR MUSEOSCRIPT EXTRA FUNSTIONALITY
extra_museoscript_mode_var = IntVar()
extra_museoscript_checkbox = Checkbutton(
    second_frame,
    text="Retrieve the original reads",
    variable=extra_museoscript_mode_var,
    bg="#fffacd",
)
extra_museoscript_checkbox.grid_forget()

# EXTRA CHECKBOX FOR MUSEOSCRIPT EXTRA FUNSTIONALITY
# extra_museoscript_mode_var = IntVar()
# extra_museoscript_checkbox = create_checkbox(second_frame, "Retrieve the original reads ", 0, 1, museoscript_mode_var,  main_frames)
# extra_museoscript_checkbox.configure(command=museoscript_widgets)
# Initially hide the widget
museo_script_output.grid_forget()
museoscript_widgets()


# Configure style for Combobox. Change method's background to from gray to white
style = Style()
style.configure(
    "TCombobox",
    fieldbackground="white",  # Field background (entry part)
    background="white",
)  # Background of the dropdown part

# Map different styles for readonly and disabled states
style.map(
    "TCombobox",
    fieldbackground=[("disabled", "lightgray")],
    background=[("disabled", "lightgray")],
    foreground=[("disabled", "gray")],
)
blast_type.configure(style="TCombobox")
###### THIRD FRAME ######

# Texts
query2 = Label(third_frame, text="Select query files", bg="#fffacd")
query2.grid(row=1, column=0, columnspan=2, sticky="w", padx=10, pady=1)
database2 = Label(third_frame, text="Select database", bg="#fffacd")
database2.grid(row=1, column=2, columnspan=2, sticky="w", padx=25, pady=1)
output2 = Label(third_frame, text="Select directory for output files", bg="#fffacd")
output2.grid(row=1, column=4, columnspan=2, sticky="w", padx=25, pady=1)


# Select query files and button
select_query2 = StringVar()
select_query2 = Entry(third_frame, width=25, textvariable=select_query2)
select_query2.grid(row=2, column=0, sticky="we", padx=(10, 5))

button1_2 = Button(
    third_frame,
    text="Browse",
    width=8,
    height=2,
    command=lambda: select_fadb_button_cmd("query", 2),
)
button1_2.grid(row=2, column=1, sticky="we", padx=(5, 25))

# Select database and button

select_db2 = StringVar()
select_db2 = Entry(third_frame, width=25, textvariable=select_db2)
select_db2.grid(row=2, column=2, sticky="we", padx=(25, 5))

button2_2 = Button(
    third_frame,
    text="Browse",
    width=8,
    height=2,
    command=lambda: select_fadb_button_cmd("database", 2),
)
button2_2.grid(row=2, column=3, sticky="we", padx=(5, 25))

# Select output file and button
select_out2 = StringVar()
select_out2 = Entry(third_frame, width=25, textvariable=select_out2)
select_out2.grid(row=2, column=4, sticky="we", padx=(25, 5))

button3_2 = Button(
    third_frame,
    text="Browse",
    width=8,
    height=2,
    command=lambda: select_directory("output"),
)
button3_2.grid(row=2, column=5, sticky="we", padx=(5, 10))

# 3d row

button_3d = Button(
    third_frame,
    text="Browse input directory\nfor batch processing",
    width=12,
    height=2,
    command=lambda: select_directory("query"),
)
button_3d.grid(row=3, column=1, sticky="we", padx=(5, 25))

# 4th row

method2 = Label(third_frame, text="Methods:", bg="#fffacd")
method2.grid(row=4, column=0, sticky="e")

blast_typeVar2 = StringVar(value="blastn")
blast_type2 = Combobox(
    third_frame, textvariable=blast_typeVar2, values=blast_typeList
)  # , font=('', 13))
blast_type2.grid(row=4, column=1, sticky="we")
# Bind the event to toggle the visibility of extra nucleotide widgets
blast_type2.bind("<<ComboboxSelected>>", switch_nucleotide_widgets)

evalue2 = Label(third_frame, text="E-value:", bg="#fffacd")
evalue2.grid(row=4, column=2, sticky="e", padx=(10, 0), pady=(10, 0))

evalue2 = Entry(third_frame, width=25)
evalue2.insert(0, "1e-5")  # Default value
evalue2.grid(row=4, column=3, sticky="we", padx=(0, 5), pady=(10, 0))

threads2 = Label(third_frame, text="Threads:", bg="#fffacd")
threads2.grid(row=4, column=4, sticky="e", padx=(10, 0), pady=(10, 0))

threads2 = Entry(third_frame, width=25)
threads2.insert(0, "4")  # Default value
threads2.grid(row=4, column=5, sticky="w", padx=(0, 10), pady=(10, 0))

### EXTRA NUCLEOTIDE WIDGET FOR BLASTX METHOD ###
extra_nucleotide_entry = Entry(third_frame, width=40)
extra_nucleotide_entry.insert(0, "Extra nucleotide file for blastx")
extra_nucleotide_browse_button = Button(
    third_frame,
    text="Browse",
    width=8,
    height=2,
    command=lambda: select_fadb_button_cmd("extra_nucleotide_file", 0),
)

# Switch function initially to set the visibility of widgets
switch_nucleotide_widgets(None)

###### FOURTH FRAME ######

# 2d row
query3 = Label(fourth_frame, text="Select query files", bg="#fffacd")
query3.grid(row=1, column=0, columnspan=6, sticky="w", padx=10, pady=1)

# Select query files and button
select_query3 = StringVar()
select_query3 = Entry(fourth_frame, width=25, textvariable=select_query3)
select_query3.grid(row=2, column=0, sticky="we", padx=(10, 5))

button1_3 = Button(
    fourth_frame,
    text="Browse",
    width=8,
    height=2,
    command=lambda: select_fadb_button_cmd("query", 3),
)
button1_3.grid(row=2, column=1, sticky="we", padx=(5, 25))

method3 = Label(fourth_frame, text="Select database type: ", bg="#fffacd")
method3.grid(row=2, column=2, sticky="we")

db_typeList = [
    "Nucleic acid sequence",
    "Protein sequence",
]
database_typeVar = StringVar()
database_type = Combobox(
    fourth_frame, textvariable=database_typeVar, values=db_typeList
)
database_type.grid(row=2, column=3, sticky="we")

database_name = Label(fourth_frame, text="Select database name: ", bg="#fffacd")
database_name.grid(row=2, column=4, sticky="w", padx=(10, 0))

database_name = Entry(fourth_frame, width=25)
database_name.grid(row=2, column=5, padx=(0, 10), sticky="we")

###### FIFTH FRAME ######

# button_help = Button(fifth_frame, text="Help", bg="#add8e6", width=8, height=2, command=main_instructions)
# button_help.grid(row=0, column=0, columnspan=3, sticky="nsew", padx=(5, 25))


# button_start = Button(fifth_frame, text="Start", bg="#90ee90", width=8, height=2, command=start_processing)
# button_start.grid(row=0, column=4, columnspan=3, sticky="nsew", padx=(5, 25))

button_help = Button(
    fifth_frame, text="Help", bg="#add8e6", width=8, height=2, command=main_instructions
)
button_help.grid(row=0, column=0, columnspan=3, sticky="nsew", padx=(15, 25), pady=10)

button_start = Button(
    fifth_frame, text="Start", bg="#90ee90", width=8, height=2, command=start_processing
)
button_start.grid(row=0, column=4, columnspan=3, sticky="nsew", padx=(15, 25), pady=10)

###############################

##### BUTTONS AND ENTRY FIELDS CONTROL #####

buttons = []
entry_widgets = []


top.mainloop()
