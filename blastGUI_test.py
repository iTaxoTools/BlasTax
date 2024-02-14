#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author：Wu Qing

import os
import re
import subprocess
from tkinter import *
from tkinter.font import Font
#from tkinter.ttk import *
from tkinter.messagebox import *
import tkinter.filedialog
import tkinter.simpledialog
from tkinter.ttk import Style
import shutil
from PIL import ImageTk, Image
from tkinter import ttk
from tkinter.ttk import Combobox


def start_processing():
    if run_blast_var.get() == 1:
        star()
    elif run_batch_var.get() == 1:
        loop_blast()
    elif build_db_var.get() == 1:
        make_db_button_cmd()

    else:
        showinfo(title='warning', message='Please select a checkbox')

def make_db_button_cmd():
        if fndb == '':
            print("Input: ", fndb)
            return showinfo(title='warning', message='The build database file is not selected!')
        if database_type.get() != 'Nucleic acid sequence' and database_type.get() != 'Protein sequence':
            return showinfo(title='warning', message='The database type is not selected!')
        if database_name.get() == '':
            return showinfo(title='warning', message='Database name is not set!')
        if database_type.get() == 'Nucleic acid sequence':
            t = 'nucl'
        if database_type.get() == 'Protein sequence':
            t = 'prot'
        n = database_name.get()
        p = subprocess.Popen(
            "makeblastdb -parse_seqids -in " + fndb + " -dbtype " + t + " -title " + n + " -out " + n,
            shell=True, stdout=subprocess.PIPE)
        p.wait()
        out = p.stdout.readlines()
        if p.returncode == 0:
            showinfo(title="info", message="Database built successfully!")
#            makedb_state.delete(0.0, END)
#            for line in out:
#                makedb_state.insert("insert", line)
        else:
            showinfo(title="info", message="Database creation failed!")
#def make_db():

#    def select_fadb_button_cmd():
#        global fndb
#        fndb = tkinter.filedialog.askopenfilename()
#        make_db_label.config(text="The files you selected:\n" + fndb)

### MAKE an Instruction depending on what checkbox is clicked

def mkdb_instruction():
        makedb_state.insert('1.0', "1. Click select file button to select FASTA file \n\n2. Select database type \n\
            \n3. Enter the name of the database (no Spaces)\n\
            \n4. Click Build database button to start database building \n\
            \n5.After the database construction is completed, please restart this program to refresh the database list")
'''
    dbwindow = Tk()
    dbwindow.title('Build database')
    dbwindow.geometry('600x400')

    mkdb_typeList = ['Nucleic acid sequence', 'Protein sequence', ]
    mkdb_type = Combobox(dbwindow, text='Nucleic acid sequence', values=mkdb_typeList, font=('', 13))
    mkdb_type.place(relx=0.394, rely=0.192, relwidth=0.251)

    makedb_stateFont = Font(font=('', 13))
    makedb_state = Text(dbwindow, font=makedb_stateFont)
    makedb_state.place(relx=0.041, rely=0.505, relwidth=0.915, relheight=0.435)
    mkdb_instruction()

    style.configure('Tmake_db_button.TButton', font=('', 13))
    make_db_button = Button(dbwindow, text='Build database', command=make_db_button_cmd, style='Tmake_db_button.TButton')
    make_db_button.place(relx=0.705, rely=0.216, relwidth=0.251, relheight=0.219)

    db_name_inputVar = StringVar(value='db')
    db_name_input = Entry(dbwindow, textvariable=db_name_inputVar, font=('', 13))
    db_name_input.place(relx=0.394, rely=0.336, relwidth=0.251, relheight=0.099)

    style.configure('Tselect_fadb_button.TButton', font=('', 13))
    select_fadb_button = Button(dbwindow, text='Select file', command=select_fadb_button_cmd, style='Tselect_fadb_button.TButton')
    select_fadb_button.place(relx=0.705, rely=0.048, relwidth=0.251, relheight=0.123)

    style.configure('Tdb_type_label.TLabel', anchor='w', font=('', 13))
    db_type_label = Label(dbwindow, text='Select database type', style='Tdb_type_label.TLabel')
    db_type_label.place(relx=0.041, rely=0.192, relwidth=0.272, relheight=0.099)

    style.configure('Tdb_name.TLabel', anchor='w', font=('', 13))
    db_name = Label(dbwindow, text='Set database name', style='Tdb_name.TLabel')
    db_name.place(relx=0.041, rely=0.336, relwidth=0.272, relheight=0.099)

    style.configure('Tmake_db_label.TLabel', anchor='center', font=('', 13))
    make_db_label = Label(dbwindow, text='You did not select any files', style='Tmake_db_label.TLabel')
    make_db_label.place(relx=0.041, rely=0.048, relwidth=0.602, relheight=0.105)

    dbwindow.mainloop()
'''

##### NEW CODE #####
def select_fadb_button_cmd(type,number):
        global fndb
        global db
        global outp
        if type == "query":
            fndb = tkinter.filedialog.askopenfilename()
            if number ==1:
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
            outp = tkinter.filedialog.askopenfilename()
            if number == 1:
                select_out.delete(0, tkinter.END)
                select_out.insert(tkinter.END, outp)
            elif number == 3:
                select_out3.delete(0, tkinter.END)
                select_out3.insert(tkinter.END, outp)

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

def get_fasta():
    input = fa_input.get()
    tmp = ''.join(re.findall(r'[A-Za-z]', input))
    if tmp == '':
        showinfo(title='warning', message='Please enter the correct sequence')
        return 1
    else:
        #tmp = str.upper(tmp)
        with open("tmp.txt", "w+") as f:
            f.write(tmp)
        return 0



# get database name list
def get_db_name():
    namelist = []
    for fn in os.listdir(os.getcwd()):
        if os.path.splitext(fn)[1] == '.phr' or os.path.splitext(fn)[1] == '.nhr':
            fn = os.path.splitext(fn)[0]
            namelist.append(fn)
    return namelist

# add up blast hits to the input files
def blast_parse(input_file,blast_result,outfile_name):
    if blast_type2.get() == "blastn":
    # copy the content of the input file to a new output file
        db_name = select_db2.get()
        db_name = db_name.rsplit("/", 1)[-1]
        blastfile = open(blast_result, "r")
        try:
            shutil.copyfile(input_file, outfile_name)
            print(f"Content of {input_file} copied to {outfile_name} successfully.")
        except IOError as e:
            print(f"Error: {e}")
    # add upp blast hits to the new output file
        outfile = open(outfile_name, "a")
        for line in blastfile:
            splitti = line.split('\t')
            print(splitti, splitti[3])
            pident = splitti[1]

            header_line = f'>{db_name}_{splitti[3]}_pident_{pident[:-2]}\n'
            sequence_line = f'{splitti[4]}\n'

            outfile.writelines([header_line, sequence_line])

        outfile.close()
        blastfile.close()

# blast process
def star(type=None,query=None):
    fnfa_stat = "The files you selected:" + fnfa
#    fain_stat = fa_input.get()
    fain_stat = select_query.get()
    if fnfa_stat == fain_stat:
        fa = fnfa
    else:
        fa = 'tmp.txt'
#    if
#        blast_q
    print("blast type; ", blast_type.get())
    print("query: ", str(select_query.get()))
    print("outfmt: ", outfmt.get())
    print("evalue: ", evalue.get())
    print("db: ", str(select_db.get()))
    print("Threads: ", threads.get())
    print("Other cmd", other.get())
    db = "/home/nkulikov/Downloads/BlastGUI-master/BlastGUI/db/mala"
    b = subprocess.Popen(str(blast_type.get()) + " -out result.txt -query " + str(select_query.get()) + " -outfmt " + str(outfmt.get()) +
                         " -evalue " + str(evalue.get()) + " -db " + str(select_db.get()) + ' -num_threads ' + str(threads.get())+
                         ' ' + str(other.get()),
                         shell=True, stdout=subprocess.PIPE)
    b.wait()

    if b.returncode == 0:
        pass
#        result_output.delete(0.0, END)
#        with open("result.txt", "r") as result:
#            for line in result:
#                result_output.insert('insert', line)
    else:
        showinfo(title='warning', message='Wrong alignment!\nPlease make sure the parameters are set correctly!')

def loop_blast():
    directory = str(select_query2.get())
    # Check if the directory exists
    if not os.path.exists(directory):
        os.makedirs(directory)
    for file in os.listdir(directory):
        if file.endswith(('.fa', '.fas','.fasta')):
            output_file = file.split('.')[0] + ".out"
            input_file = os.path.join(directory,file)
            output_file = os.path.join(str(select_out2.get()),output_file)
            print("db: ", select_db2.get())

            print("inpit file: ", input_file)
            b=subprocess.Popen(
                    f"{blast_type2.get()} -out {output_file} -query {input_file} -outfmt '{int(6)} length pident qseqid sseqid sseq qframe sframe' "
                    f"-evalue {evalue2.get()} -db {select_db2.get()} -num_threads {int(threads2.get())}",
                    shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            b.wait()

            if b.returncode == 0:
                print("BLAST execution successful.")
                # Print the content of the output file
                with open(output_file, 'r') as f:
                    print("Content of the output file:")
                    print(f.read())

            else:
                showinfo(title='warning',
                         message='Wrong alignment!\nPlease make sure the parameters are set correctly!')
        # modification of output files
#          filesplit = input_file.rsplit("/", 1)[-1]
            filesplit = file.split('.')
            modified_output = filesplit[0] + '_blastmatchesadded.' + filesplit[1]
            modified_output =  os.path.join(str(select_out2.get()),modified_output)
            blast_parse(input_file, output_file, modified_output)


def star_blast_cmd():
    try:
        os.remove((os.path.join(os.getcwd(), 'tmp.txt')))
        os.remove((os.path.join(os.getcwd(), 'result.txt')))
    finally:
        if get_fasta() == 1:
            return 1
        if get_fasta() == 0:
            star()
            return 0


def select_fa_button_Cmd():
    global fnfa
    fnfa = tkinter.filedialog.askopenfilename()
    query_sequence.delete(0, END)
    if fnfa != '':
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
    lbl = Label(top, text="Instructions:\n\n1. Please click the [Build database] button to set up the database for the first time\n \
    \n2.Input the sequence to be aligned into the text box or select the sequence file through the [Select file] button \
     \n\n3.Select the database to be compared and the comparison method.\n\n4.Set the e-value Value, output format and number of threads.The default e-value =1e-5, and the default output format is 0 and the default of threads is 4\n \
     \n5.(Optional) Any other command of BLAST like: -max_target_seqs 20 \n\n6.Click [Start] button for comparison, and the comparison results will be displayed here and saved in result.txt\n\n7.Alignment time depends on sequence size and computer performance \
     \n").pack()
    btn2 = Button(top,text="Close help message",command=top.destroy).pack()

### Checkbox control functions
def on_checkbox_click(frame, checkbox, all_frames):
    state = checkbox.var.get()
    for other_frame in all_frames:
        if other_frame != frame:
            for widget in other_frame.winfo_children():
                widget.configure(state='disable' if state == 1 else 'normal')

def create_checkbox(frame, text, row, column, variable, all_frames):
    checkbox = Checkbutton(frame, text=text, bg="#fffacd", onvalue=1, offvalue=0, variable=variable)
    checkbox.grid(row=row, column=column, columnspan=6, sticky="w", padx=(6, 0), pady=1)
    checkbox.var = variable
    checkbox.configure(command=lambda: on_checkbox_click(frame, checkbox, all_frames))
    return checkbox


#def mkdb_window_cmd():
#    make_db()

###GUI part of the program ###
top = Tk()
top.title('BlAST-Align')
top.geometry('960x560')

#top.rowconfigure(0, weight=1)  # Add a configuration for the first row
top.rowconfigure(1, weight=1)
top.rowconfigure(2, weight=1)
top.rowconfigure(3, weight=1)
top.rowconfigure(4, weight=1)
#top.rowconfigure(2, weght=1)
#top.rowconfigure(3, weight=1)
top.columnconfigure(0, weight=1)

style = Style()
fnfa = ''
fndb = ''

### CREATE MAIN FRAMES ###
banner_frame = LabelFrame(top,bg="#f0f0f0")

second_frame = LabelFrame(top,bg="#fffacd")
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

third_frame = LabelFrame(top,bg="#fffacd")
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

fourth_frame = LabelFrame(top,bg="#fffacd")
fourth_frame.grid(column=0, row=3, sticky="nsew")
fourth_frame.columnconfigure(0, weight=1)
fourth_frame.columnconfigure(1, weight=1)
fourth_frame.columnconfigure(2, weight=1)
fourth_frame.columnconfigure(3, weight=1)
fourth_frame.columnconfigure(4, weight=1)
fourth_frame.columnconfigure(5, weight=1)

fifth_frame = LabelFrame(top,bg="#fffacd")
fifth_frame.grid(column=0, row=4, sticky="nsew")
fifth_frame.columnconfigure(0, weight=1)
fifth_frame.columnconfigure(4, weight=1)


### CHECKBOXES ###
main_frames = [second_frame, third_frame, fourth_frame]
run_blast_var = IntVar()
run_blast_checkbox = create_checkbox(second_frame, "Run regular BLAST", 0, 0, run_blast_var,  main_frames)

run_batch_var = IntVar()
run_batch_checkbox = create_checkbox(third_frame, "Run batch BLAST-Align", 0, 0, run_batch_var, main_frames)

build_db_var = IntVar()
run_batch_checkbox3 = create_checkbox(fourth_frame, "Build BLAST database", 0, 0, build_db_var, main_frames)

### Title Frame ###
banner_frame = LabelFrame(top,bg="#f0f0f0")
banner_img = ImageTk.PhotoImage(Image.open("iTaxoTools Digital linneaeus MICROLOGO.png"))


my_image_label = Label(banner_frame, image=banner_img).grid(row=0, column=0, rowspan=3, sticky="nsew")
banner_frame.grid(column=0, row=0,  sticky="nsew")

program_name = Label(banner_frame, text="BlAST-Align",bg="#f0f0f0",font=Font(size=20))
program_name.grid(row=1, column=1)
program_description = Label(banner_frame, text="Add sequences to alignment if matching in Blast search",bg="#f0f0f0")
program_description.grid(row=1, column=2,  sticky="nsew", ipady=4, ipadx=15)

author = Label(banner_frame, text="Code by Nikita Kulikov, Anja-Kristina Schulz and Stefanos Patmanidis \nGUI modified from BLAST-GUI by Du et al. (2020) / https://github.com/byemaxx/BlastGUI",
        font=Font(size=8),bg="#f0f0f0")
author.grid(row=2, column=1, columnspan=2,  sticky="w")


###### SECOND FRAME ######

# Texts
query = Label(second_frame, text="Select query files",bg="#fffacd")
query.grid(row=1, column=0, columnspan=2,sticky="w",padx=10,pady=1)
database = Label(second_frame, text="Select database",bg="#fffacd")
database.grid(row=1, column=2, columnspan=2,sticky="w",padx=25,pady=1)
output = Label(second_frame, text="Select output file",bg="#fffacd")
output.grid(row=1, column=4, columnspan=2,sticky="w",padx=25,pady=1)
# Select query files and button
select_query = StringVar()
select_query = Entry(second_frame,width=25,textvariable=select_query)
select_query.grid(row=2, column=0, sticky="we", padx=(10, 5))

button1 = Button(second_frame, text="Browse",  width=8, height=2, command=lambda: select_fadb_button_cmd("query",1))
button1.grid(row=2, column=1, sticky="we", padx=(5, 25))

# Select database and button

select_db = StringVar()
select_db = Entry(second_frame, width=25, textvariable=select_db)
select_db.grid(row=2, column=2, sticky="we", padx=(25, 5))

button2 = Button(second_frame, text="Browse",  width=8, height=2, command=lambda: select_fadb_button_cmd("database",1))
button2.grid(row=2, column=3, sticky="we", padx=(5, 25))

# Select output file and button
select_out = StringVar()
select_out = Entry(second_frame, width=25, textvariable=select_out)
select_out.grid(row=2, column=4, sticky="we", padx=(25, 5))

button3 = Button(second_frame, text="Browse", width=8, height=2,command=lambda: select_fadb_button_cmd("output",1))
button3.grid(row=2, column=5, sticky="we", padx=(5, 10))

#Text
# New label in the next row
third_row = Label(second_frame, text="Or paste query sequence here:",bg="#fffacd")
third_row.grid(row=3, column=0, columnspan=6, sticky="w",padx=10)

### next row

# New row with input fields and labels
query_sequence = Entry(second_frame, width=25,font=16,)
query_sequence.grid(row=4, column=0, columnspan=2, sticky="we", padx=(10, 10), pady=(10, 0))

evalue = Label(second_frame, text="E-value:",bg="#fffacd")
evalue.grid(row=4, column=2, sticky="e", padx=(10,0), pady=(10, 0))

evalue = Entry(second_frame, width=25)
evalue.insert(0, "1e-5")  # Default value
evalue.grid(row=4, column=3, sticky="we", padx=(0, 5), pady=(10, 0))

threads = Label(second_frame, text="Threads:",bg="#fffacd")
threads.grid(row=4, column=4, sticky="e", padx=(10,0), pady=(10, 0))

threads = Entry(second_frame, width=25)
threads.insert(0, "4")  # Default value
threads.grid(row=4, column=5, sticky="we", pady=(10, 0))

# next row
outfmt = Label(second_frame, text="Outfmt:",bg="#fffacd")
outfmt.grid(row=5, column=0, sticky="e", padx=(10,0), pady=(10, 0))

outfmt = Entry(second_frame, width=25)
outfmt.insert(0, "0")  # Default value
outfmt.grid(row=5, column=1, sticky="we", padx=(0, 5), pady=(10, 0))

other = Label(second_frame, text="Other cmd:",bg="#fffacd")
other.grid(row=5, column=2, sticky="e", padx=(10,0), pady=(10, 0))

other = Entry(second_frame, width=25)
other.grid(row=5, column=3, sticky="we", pady=(10, 0))

# Last row

method = Label(second_frame, text="Methods:",bg="#fffacd")
method.grid(row=5, column=4, sticky="e")

blast_typeList = ['blastn', 'blastp', 'blastx', 'tblastn', 'tblastx', ]
blast_typeVar = StringVar(value='blastn')
blast_type = Combobox(second_frame, textvariable=blast_typeVar, values=blast_typeList, font=('', 13))
blast_type.grid(row=5, column=5, sticky="w")

###############################

###### THIRD FRAME ######

# Texts
query2 = Label(third_frame, text="Select query files",bg="#fffacd")
query2.grid(row=1, column=0, columnspan=2,sticky="w",padx=10,pady=1)
database2 = Label(third_frame, text="Select database",bg="#fffacd")
database2.grid(row=1, column=2, columnspan=2,sticky="w",padx=25,pady=1)
output2 = Label(third_frame, text="Select directory for output files",bg="#fffacd")
output2.grid(row=1, column=4, columnspan=2,sticky="w",padx=25,pady=1)


# Select query files and button
select_query2 = StringVar()
select_query2 = Entry(third_frame,width=25,textvariable=select_query2)
select_query2.grid(row=2, column=0, sticky="we", padx=(10, 5))

button1_2 = Button(third_frame, text="Browse",  width=8, height=2, command=lambda: select_fadb_button_cmd("query",2))
button1_2.grid(row=2, column=1, sticky="we", padx=(5, 25))

# Select database and button

select_db2 = StringVar()
select_db2 = Entry(third_frame, width=25, textvariable=select_db2)
select_db2.grid(row=2, column=2, sticky="we", padx=(25, 5))

button2_2 = Button(third_frame, text="Browse",  width=8, height=2, command=lambda: select_fadb_button_cmd("database",2))
button2_2.grid(row=2, column=3, sticky="we", padx=(5, 25))

# Select output file and button
select_out2 = StringVar()
select_out2 = Entry(third_frame, width=25, textvariable=select_out2)
select_out2.grid(row=2, column=4, sticky="we", padx=(25, 5))

button3_2 = Button(third_frame, text="Browse", width=8, height=2,command=lambda: select_directory("output"))
button3_2.grid(row=2, column=5, sticky="we", padx=(5, 10))

# 3d row

button_3d = Button(third_frame, text="Browse input directory\nfor batch conversions", width=12, height=2, command=lambda: select_directory("query"))
button_3d.grid(row=3, column=1, sticky="we", padx=(5, 25))

# 4th row

method2 = Label(third_frame, text="Methods:",bg="#fffacd")
method2.grid(row=4, column=0, sticky="e")

blast_typeVar2 = StringVar(value='blastn')
blast_type2 = Combobox(third_frame, textvariable=blast_typeVar2, values=blast_typeList, font=('', 13))
blast_type2.grid(row=4, column=1, sticky="we")

evalue2 = Label(third_frame, text="E-value:",bg="#fffacd")
evalue2.grid(row=4, column=2, sticky="e", padx=(10,0), pady=(10, 0))

evalue2 = Entry(third_frame, width=25)
evalue2.insert(0, "1e-5")  # Default value
evalue2.grid(row=4, column=3, sticky="we", padx=(0, 5), pady=(10, 0))

threads2 = Label(third_frame, text="Threads:",bg="#fffacd")
threads2.grid(row=4, column=4, sticky="e", padx=(10,0), pady=(10, 0))

threads2 = Entry(third_frame, width=25)
threads2.insert(0, "4")  # Default value
threads2.grid(row=4, column=5, sticky="w", pady=(10, 0))



###### FOURTH FRAME ######

# 2d row
query3 = Label(fourth_frame, text="Select query files",bg="#fffacd")
query3.grid(row=1, column=0, columnspan=6,sticky="w",padx=10,pady=1)

# Select query files and button
select_query3 = StringVar()
select_query3 = Entry(fourth_frame,width=25,textvariable=select_query3)
select_query3.grid(row=2, column=0, sticky="we", padx=(10, 5))

button1_3 = Button(fourth_frame, text="Browse",  width=8, height=2, command=lambda: select_fadb_button_cmd("query",3))
button1_3.grid(row=2, column=1, sticky="we", padx=(5, 25))

method3 = Label(fourth_frame, text="Select database type: ",bg="#fffacd")
method3.grid(row=2, column=2, sticky="we")

db_typeList = ['Nucleic acid sequence', 'Protein sequence', ]
database_typeVar = StringVar()
database_type = Combobox(fourth_frame, textvariable=database_typeVar,values=db_typeList)
database_type.grid(row=2, column=3, sticky="we")

database_name = Label(fourth_frame, text="Select database name: ",bg="#fffacd")
database_name.grid(row=2, column=4, sticky="w", padx=(10,0))

database_name = Entry(fourth_frame, width=25)
database_name.grid(row=2, column=5, sticky="we")

###### FIFTH FRAME ######

button_help = Button(fifth_frame, text="Help", bg="#add8e6", width=8, height=2, command=main_instructions)
button_help.grid(row=0, column=0, columnspan=3, sticky="nsew", padx=(5, 25))


button_start = Button(fifth_frame, text="Start", bg="#90ee90", width=8, height=2, command=start_processing)
button_start.grid(row=0, column=4, columnspan=3, sticky="nsew", padx=(5, 25))
###############################

##### BUTTONS AND ENTRY FIELDS CONTROL #####

buttons = []
entry_widgets = []

'''

db_typeList = get_db_name()
db_type = Combobox(top, text='Select', values=db_typeList, font=('', 13))
db_type.place(relx=0.129, rely=0.106, relwidth=0.11)

blast_typeList = ['blastn', 'blastp', 'blastx', 'tblastn', 'tblastx', ]
blast_typeVar = StringVar(value='blastn')
blast_type = Combobox(top, textvariable=blast_typeVar, values=blast_typeList, font=('', 13))
blast_type.place(relx=0.386, rely=0.1, relwidth=0.08)

reault_scroll1 = Scrollbar(top, orient='vertical')
reault_scroll1.place(relx=0.959, rely=0.212, relwidth=0.031, relheight=0.758)

evalueVar = StringVar(value='1e-5')
evalue = Entry(top, textvariable=evalueVar, font=('', 12))
evalue.place(relx=0.129, rely=0.166, relwidth=0.11, relheight=0.034)

result_outputFont = Font(font=('', 13))
result_output = Text(top, yscrollcommand=reault_scroll1.set, font=result_outputFont)
result_output.place(relx=0.02, rely=0.212, relwidth=0.931, relheight=0.773)
main_instructions()
reault_scroll1['command'] = result_output.yview

#star_blastVar = StringVar(value='Start')
#style.configure('Tstar_blast.TButton', background='#000000', font=('', 13))
#star_blast = Button(top, text='Start', textvariable=star_blastVar, command=star_blast_cmd, style='Tstar_blast.TButton')
#star_blast.place(relx=0.791, rely=0.015, relwidth=0.08, relheight=0.138)


#style.configure('Tselect_fa_button.TButton', background='#000000', font=('', 13))
#select_fa_button = Button(top, text='Select\n   file', command=select_fa_button_Cmd,
#                          style='Tselect_fa_button.TButton')
#select_fa_button.place(relx=0.692, rely=0.015, relwidth=0.09, relheight=0.138)

# main enter bar
#fa_inputVar = StringVar(value='Enter a sequence here or select a sequence file:')
#fa_input = Entry(top, textvariable=fa_inputVar, font=('', 13))
#fa_input.place(relx=0.02, rely=0.015, relwidth=0.654, relheight=0.078)

#aboutVar = StringVar(value='About')
#style.configure('Tabout.TButton', font=('', 13))
#about = Button(top, text='About', textvariable=aboutVar, command=about_cmd, style='Tabout.TButton')
#about.place(relx=0.88, rely=0.015, relwidth=0.11, relheight=0.065)

#mkdb_windowVar = StringVar(value=' Build\ndatabase')
#style.configure('Tmkdb_window.TButton', font=('', 13))
#mkdb_window = Button(top, text='Build database', textvariable=mkdb_windowVar, command=mkdb_window_cmd, style='Tmkdb_window.TButton')
#mkdb_window.place(relx=0.88, rely=0.091, relwidth=0.11, relheight=0.065)

evalue_labelVar = StringVar(value='E-value：')
style.configure('Tevalue_label.TLabel', anchor='w', font=('', 12))
evalue_label = Label(top, text='E-value', textvariable=evalue_labelVar, style='Tevalue_label.TLabel')
evalue_label.place(relx=0.02, rely=0.166, relwidth=0.09, relheight=0.032)

blast_select_labelVar = StringVar(value='Methods：')
style.configure('Tblast_select_label.TLabel', anchor='w', font=('', 12))
blast_select_label = Label(top, text='Methods', textvariable=blast_select_labelVar, style='Tblast_select_label.TLabel')
blast_select_label.place(relx=0.267, rely=0.106, relwidth=0.09, relheight=0.032)

db_selectVar = StringVar(value='Database:')
style.configure('Tdb_select.TLabel', anchor='w', font=('', 12))
db_select = Label(top, text='Database', textvariable=db_selectVar, style='Tdb_select.TLabel')
db_select.place(relx=0.02, rely=0.106, relwidth=0.09, relheight=0.032)

outfmt_labelVar = StringVar(value='Outfmt:')
style.configure('Toutfmt_label.TLabel', anchor='w', font=('', 12))
outfmt_label = Label(top, text='Outfmt', textvariable=outfmt_labelVar, style='Toutfmt_label.TLabel')
outfmt_label.place(relx=0.267, rely=0.166, relwidth=0.09, relheight=0.032)

outfmt_inputVar = StringVar(value='0')
outfmt_input = Entry(top, textvariable=outfmt_inputVar, font=('', 12))
outfmt_input.place(relx=0.386, rely=0.166, relwidth=0.08, relheight=0.034)

threat_labelVar = StringVar(value='Threads:')
style.configure('Tthreat_label.TLabel', anchor='w', font=('', 12))
threat_label = Label(top, text='Threads:', textvariable=threat_labelVar, style='Tthreat_label.TLabel')
threat_label.place(relx=0.494, rely=0.106, relwidth=0.08, relheight=0.032)

threat_inputVar = StringVar(value='4')
threat_input = Entry(top, textvariable=threat_inputVar, font=('', 12))
threat_input.place(relx=0.593, rely=0.106, relwidth=0.08, relheight=0.034)

othercmd_labelVar = StringVar(value='Other cmd:')
style.configure('Tothercmd_label.TLabel', anchor='w', font=('', 12))
othercmd_label = Label(top, text='other cmd', textvariable=othercmd_labelVar, style='Tothercmd_label.TLabel')
othercmd_label.place(relx=0.494, rely=0.166, relwidth=0.08, relheight=0.032)

othercmd_inputVar = StringVar(value=' ')
othercmd_input = Entry(top, textvariable=othercmd_inputVar, font=('', 12))
othercmd_input.place(relx=0.593, rely=0.166, relwidth=0.19, relheight=0.034)
'''
top.mainloop()
