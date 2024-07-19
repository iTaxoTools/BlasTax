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
from tkinter import filedialog

def start_processing():
    if run_blast_var.get() == 1:
        star()
    elif run_batch_var.get() == 1:
        loop_blast()
    elif build_db_var.get() == 1:
        make_db_button_cmd()

    else:
        showinfo(title='warning', message='Please select a checkbox')


def check_fasta_headers(file_path):
    """Check if any header in the FASTA file is longer than 51 characters or contains special characters, allowing underscores and '>'."""
    # Define invalid characters as a regex pattern (excluding underscores and '>')
    invalid_chars_pattern = re.compile(r'[^\w\s>]')

    with open(file_path, 'r') as file:
        for line in file:
            if line.startswith('>'):  # Header line starts with '>'
                header = line.strip()
                if len(header) > 51:
                    return "length"
                if invalid_chars_pattern.search(header):
                    return "special"

def make_db_button_cmd():
        if fndb == '':
            print("Input: ", fndb)
            return showinfo(title='warning', message='The build database file is not selected!')
        if database_type.get() != 'Nucleic acid sequence' and database_type.get() != 'Protein sequence':
            return showinfo(title='warning', message='The database type is not selected!')
        if database_name.get() == '':
            return showinfo(title='warning', message='Database name is not set!')
        header_check_result = check_fasta_headers(fndb)
        if header_check_result == "length":
            return showinfo(title='warning',
                            message='One or more sequence headers in the FASTA file exceed 51 characters! Please check and edit headers!')
        elif header_check_result == "special":
            return showinfo(title='warning',
                            message='One or more sequence headers in the FASTA file contain special characters! Please check and edit headers!')
        if database_type.get() == 'Nucleic acid sequence':
            t = 'nucl'
        if database_type.get() == 'Protein sequence':
            t = 'prot'

        # Extract directory path from fndb
        directory_path = os.path.dirname(fndb)
        # Define the output filename
        output_filename_db = os.path.join(directory_path, database_name.get())

        n = database_name.get()
        p = subprocess.Popen(
            "makeblastdb -parse_seqids -in " + fndb + " -dbtype " + t + " -title " + n + " -out " + output_filename_db,
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

### CREATE A NEW OUTPUT FILE FOR THE REGULAR BLAST ###
def get_new_filename():
    new_filename = filedialog.asksaveasfilename(defaultextension=".out", filetypes=[("Text files", "*.txt")])
    return new_filename

### BROWSE FILES ###
def select_fadb_button_cmd(type,number):
        global fndb
        global db
        global outp
        global extnucl
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
            if number == 1:
                outp = get_new_filename()
                select_out.delete(0, tkinter.END)
                select_out.insert(tkinter.END, outp)
            elif number == 3:
                outp = tkinter.filedialog.askopenfilename()
                select_out3.delete(0, tkinter.END)
                select_out3.insert(tkinter.END, outp)
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
# remove all gaps from the input files
def remove_gaps(input,temporary):
    with open(input, 'r') as infile, open(temporary, 'w') as outfile:
        for line in infile:
            if not line.startswith(">"):
                modified_line = line.replace("-", "")
                outfile.write(modified_line)
            else:
                outfile.write(line)

# keep only the hit with the highest length and hisghets match score
def output_preprocessing():
    pass



### EXTRA NUCLEOTIDE FILE WIDGETS FOR LOOP-BLASTX ###
def switch_nucleotide_widgets(state):
    if blast_typeVar2.get() == 'blastx':
        # Make the widgets for extra nucleotide file active
        extra_nucleotide_entry.grid(row=3, column=2, sticky="we", pady=(10, 0))
        extra_nucleotide_browse_button.grid(row=3, column=3, sticky="we", padx=(5, 25), pady=(10, 0))
    else:
        # Remove or hide the widgets for extra nucleotide file
        extra_nucleotide_entry.grid_forget()
        extra_nucleotide_browse_button.grid_forget()

### EXTRA WIDGETS if museoscript mode was chosen
def museoscript_widgets():
    if museoscript_mode_var.get():
        # Make the widgets for museoscript output file
        museoscript_parameters.grid(row=6, column=0, columnspan=2, sticky="w", pady=(10, 0), padx=(10, 5))
        similarity_threshold_label.grid(row=7, column=0, sticky="e", pady=(10, 0), padx=(10, 5))
        similarity_threshold_entry.grid(row=7, column=1, sticky="w", pady=(10, 0), padx=(0, 25))
        museo_script_output_text.grid(row=7, column=2, columnspan=2, sticky="e", pady=(10, 0), padx=(25, 5))
        museo_script_output.grid(row=7, column=4, sticky="w", pady=(10, 0), padx=(0, 5))

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
        blast_typeVar.set('blastn')
        blast_type.config(state="disabled")

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


### LOOP-BLASTX FILE POSTPROCESSING ###
# FUNKTIONEN TRANSLATE
# Triplett Zuordnung AS
def trans_triplett(triplett):
    # Dictionary mapping triplet codes to amino acids
    codon_map = {
        'TTT': 'F', 'TTC': 'F', 'TTA': 'L', 'TTG': 'L',
        'TCT': 'S', 'TCC': 'S', 'TCA': 'S', 'TCG': 'S',
        'TAT': 'Y', 'TAC': 'Y', 'TAA': 'X', 'TAG': 'X',
        'TGT': 'C', 'TGC': 'C', 'TGA': 'X', 'TGG': 'W',
        'CTT': 'L', 'CTC': 'L', 'CTA': 'L', 'CTG': 'L',
        'CCT': 'P', 'CCC': 'P', 'CCA': 'P', 'CCG': 'P',
        'CAT': 'H', 'CAC': 'H', 'CAA': 'Q', 'CAG': 'Q',
        'CGT': 'R', 'CGC': 'R', 'CGA': 'R', 'CGG': 'R',
        'ATT': 'I', 'ATC': 'I', 'ATA': 'I', 'ATG': 'M',
        'ACT': 'T', 'ACC': 'T', 'ACA': 'T', 'ACG': 'T',
        'AAT': 'N', 'AAC': 'N', 'AAA': 'K', 'AAG': 'K',
        'AGT': 'S', 'AGC': 'S', 'AGA': 'R', 'AGG': 'R',
        'GTT': 'V', 'GTC': 'V', 'GTA': 'V', 'GTG': 'V',
        'GCT': 'A', 'GCC': 'A', 'GCA': 'A', 'GCG': 'A',
        'GAT': 'D', 'GAC': 'D', 'GAA': 'E', 'GAG': 'E',
        'GGT': 'G', 'GGC': 'G', 'GGA': 'G', 'GGG': 'G'
    }
#    print("AMINO ACID: ", codon_map.get(triplett))
    return codon_map.get(triplett, 'X')

def complement(seq):
	comp=''
	for i in range (0,len(seq)):
		if seq[i]=='A':
			comp=comp+'T'
		elif seq[i]=='T':
			comp=comp+'A'
		elif seq[i]=='G':
			comp=comp+'C'
		elif seq[i]=='C':
			comp=comp+'G'
	return(comp)

def translate(line):
	prot_list=[]
	ami_string_frame1=''
	for i in range(0,len(line)-1,3):
		ami=trans_triplett(line[i:i+3])
		ami_string_frame1=ami_string_frame1+ami
	prot_list.append(ami_string_frame1)
	ami_string_frame2=''
	for i in range(1,len(line)-3,3):
		ami=trans_triplett(line[i:i+3])
		ami_string_frame2=ami_string_frame2+ami
	prot_list.append(ami_string_frame2)
	ami_string_frame3=''
	for i in range(2,len(line)-3,3):
		ami=trans_triplett(line[i:i+3])
		ami_string_frame3=ami_string_frame3+ami
	prot_list.append(ami_string_frame3)
	compi=complement(line)
	reverse=compi[::-1]
	ami_string_frame1r=''
	for i in range(0,len(reverse)-1,3):
		ami=trans_triplett(reverse[i:i+3])
		ami_string_frame1r=ami_string_frame1r+ami
	prot_list.append(ami_string_frame1r)
	ami_string_frame2r=''
	for i in range(1,len(reverse)-3,3):
		ami=trans_triplett(reverse[i:i+3])
		ami_string_frame2r=ami_string_frame2r+ami
	prot_list.append(ami_string_frame2r)
	ami_string_frame3r=''
	for i in range(2,len(reverse)-3,3):
		ami=trans_triplett(reverse[i:i+3])
		ami_string_frame3r=ami_string_frame3r+ami
	prot_list.append(ami_string_frame3r)
	return(prot_list)
# ENDE TRANSLATE
def blastx_parse(infile_name,resultfile_name,outfile_name,infile2_name,db_name):
    infile = open(infile_name, "r")
    infile2 = open(infile2_name, "r")
    resultfile = open(resultfile_name, "r")
    outfile = open(outfile_name, "w")

    # Query-Sequences into output file
    for line in infile:
        outfile.write(line)

    sseqid_list = []
    for line in resultfile:
        splitti = line.split('\t')
        sseqid_list.append(splitti[3])
    name_list = []
    for eintrag in sseqid_list:
        #	elem=eintrag.split('|')
        #	print(elem[2])
        name_list.append(eintrag)
    ns_list = []
    labels = []
    for nam in name_list:
        nam_split = nam.split('_')
        if nam_split[0] in ns_list:
            labels.append(nam_split[0])
        ns_list.append(nam_split[0])

    resultfile.close()
    resultfile = open(resultfile_name, "r")

    infile.close()
    infile = open(infile_name, "a")
    # de-duplication
    dict_head_pident53 = {}
    dict_head_seq53 = {}
    dict_head_pident35 = {}
    dict_head_seq35 = {}
    dict_53_added = {}
    dict_35_added = {}
    # good hits are appended to the query sequences
    for line in resultfile:
#        print("BLAST OUTPUT LINE: ", line)
        splitti = line.split('\t')
        pident = splitti[1]
#        print("SPLITTI 3: ", splitti[3])
        if (float(pident) >= 70.) and (float(splitti[0]) >= 100.):
            infile2 = open(infile2_name, "r")
            for line2 in infile2:
                # Added. needed to be checked
                line2 = line2.replace(" ","_")
#                print("ADDITIONAL FILE LINE: ", line2)
                if splitti[3] in line2:
                    seq = infile2.readline()
                    print(seq)
            infile2.close()
#            outfile.write('>' + db_name + '_' + splitti[3] + '_' + 'pident' + '_' + pident[:-2] + '\n')
#            outfile.write(seq + '\n')
            if (len(seq) % 3) != 0:
                print('len', len(seq), seq)
            erg = translate(seq)
            r53 = erg[0:3]
            r35 = erg[3:]
            print('auftei', erg)
            print('auftei', r53, r35)

            for orient in r53:
                index = orient.find(splitti[4])
                print('ori', len(orient), len(splitti[4]), orient, index, splitti[4])
                if index >= 0:
                    # Determine the offset based on index
                    offset = index * 3 if index == 0 else (index * 3) + 1

                    # Prepare unique keys for dict_53_added
                    shorter_pident = f'>{db_name}_{splitti[3]}_pident_'
                    head_pident53_added = f'>{db_name}_{splitti[3]}_pident_{pident[:-2]}\n'
                    head_seq53_added = seq[offset:((len(splitti[4]) * 3) + offset)] + '\n'
                    any_key_starting_with_prefix = next((key for key in dict_53_added if key.startswith(shorter_pident)), None)
#                    print("HEADER SHORT: ", shorter_pident)
#                    print("HEADER: ", head_pident53_added)
#                    print("SEQUENCE: ", head_seq53_added)
#                    print("HEADER FROM DICT: ", any_key_starting_with_prefix)


                    if any_key_starting_with_prefix:
                        existing_seq_length = len(dict_53_added[any_key_starting_with_prefix])
                        new_seq_length = len(head_seq53_added)
#                        print("SEQ LENGTHS: ", existing_seq_length, "\t", new_seq_length)
                        if new_seq_length > existing_seq_length:
                            removed_value = dict_53_added.pop(any_key_starting_with_prefix, None)
#                            print("The sequence was removed: ", removed_value)
                            dict_53_added[head_pident53_added] = head_seq53_added
                        elif new_seq_length == existing_seq_length:
                            old_pident53 = float(any_key_starting_with_prefix.split("_")[-1].rstrip())
                            new_pident53 = float(head_pident53_added.split("_")[-1].rstrip())
#                            print("OLD PIDENT: ", old_pident53)
#                            print("NEW PIDENT: ", new_pident53)
                            if new_pident53 > old_pident53:
                                removed_value = dict_53_added.pop(any_key_starting_with_prefix, None)
#                                print("The sequence was removed: ", removed_value)
                                dict_53_added[head_pident53_added] = head_seq53_added
                        else:
                            continue
                    else:
                        dict_53_added[head_pident53_added] = head_seq53_added

            for orient in r35:
                index = orient.find(splitti[4])
                print('ori',len(orient),len(splitti[4]),orient,index,splitti[4])
                if index > 0:
                    offset = (index * 3) + 1
                elif index == 0:
                    offset = (index * 3)
                if index >= 0:
                    compiseq = complement(seq)
                    fragment = compiseq[offset:((len(splitti[4]) * 3) + offset)]
                    revcompseq = fragment[::-1]
                    # deduplication
                    shorter_pident = f'>{db_name}_{splitti[3]}_pident_'
                    head_pident35_added = f'>{db_name}_{splitti[3]}_pident_{pident[:-2]}\n'
                    head_seq35_added = revcompseq + '\n'
                    any_key_starting_with_prefix = next((key for key in dict_35_added if key.startswith(shorter_pident)), None)

                    if any_key_starting_with_prefix:
                        existing_seq_length = len(dict_35_added[any_key_starting_with_prefix])
                        new_seq_length = len(head_seq35_added)
#                        print("SEQ LENGTHS: ", existing_seq_length, "\t", new_seq_length)
                        if new_seq_length > existing_seq_length:
                            removed_value = dict_35_added.pop(any_key_starting_with_prefix, None)
#                            print("The sequence was removed: ", removed_value)
                            dict_35_added[head_pident35_added] = head_seq35_added
                        elif new_seq_length == existing_seq_length:
                            old_pident35 = float(any_key_starting_with_prefix.split("_")[-1].rstrip())
                            new_pident35 = float(head_pident35_added.split("_")[-1].rstrip())
#                            print("OLD PIDENT: ", old_pident53)
#                            print("NEW PIDENT: ", new_pident53)
                            if new_pident35 > old_pident35:
                                removed_value = dict_35_added.pop(any_key_starting_with_prefix, None)
#                                print("The sequence was removed: ", removed_value)
                                dict_35_added[head_pident35_added] = head_seq35_added
                        else:
                            continue
                    else:
                        dict_35_added[head_pident35_added] = head_seq35_added

    for header, sequence in dict_53_added.items():
                    outfile.write(f'{header}{sequence}')
    for header, sequence in dict_35_added.items():
         outfile.write(f'{header}{sequence}')

    infile.close()
    outfile.close()
    resultfile.close()



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
        dict_head_pident = {}
        dict_head_seq = {}
#        list_of_headers = []
        for line in blastfile:
            splitti = line.split('\t')
            print(splitti, splitti[3])
            pident = splitti[1]

#            header_line = f'>{db_name}_{splitti[3]}_pident_{pident[:-2]}\n'
            sequence_line = f'{splitti[4]}\n'

            short_header = f'>{db_name}_{splitti[3]}'

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
            outfile.write(f'{header}_pident_{dict_head_pident[header]}\n{sequence}')

        outfile.close()
        blastfile.close()

def museoscript_parse(blast_out,museo_out,pident_thr):
    museo = open(museo_out,"w")
    blast = open(blast_out,"r")

    for line in blast:
        splitti = line.split('\t')
        pident = splitti[4]

        if float(pident) >= pident_thr:
            sequence_line = f'{splitti[5]}'
            header = f'>{splitti[0]}_{splitti[1]}_{pident}\n'
            museo.write(header)
            museo.write(sequence_line)


    museo.close()
    blast.close()

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
    db = str(select_db.get().rsplit('.',1)[0])
    #db = "/home/nkulikov/Downloads/BlastGUI-master/BlastGUI/db/mala"
    # remove gaps 
    input_file = str(select_query.get())
    file_name, file_extension = input_file.rsplit('.', 1)
    temporary_file  = file_name + "_tmp." + file_extension
    remove_gaps(input_file, temporary_file)
#    b = subprocess.Popen(str(blast_type.get()) + " -out " + str(select_out.get()) + " -query " + temporary_file + " -outfmt " + str(outfmt.get()) + " " +  str(other.get()) +
#                         " -evalue " + str(evalue.get()) + " -db " + db + ' -num_threads ' + str(threads.get()),
#                         shell=True, stdout=subprocess.PIPE)
#    b.wait()

    command = (
        f"{blast_type.get()} -out {output_file_blast} -query {temporary_file} "
        f"-evalue {evalue.get()} -db {db} -num_threads {threads.get()} -outfmt '{outfmt.get()} {other.get()}'"
    )

    b = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
    b.wait()

    if b.returncode == 0:
        pass
#        result_output.delete(0.0, END)
#        with open("result.txt", "r") as result:
#            for line in result:
#                result_output.insert('insert', line)
    else:
        showinfo(title='warning', message='Wrong alignment!\nPlease make sure the parameters are set correctly!')

    if museoscript_mode_var.get() == 1: # museoscript checkbox selected
#        base, ext = os.path.splitext(select_out.get())
#        museo_filename  = f"{base}_matching_reads{ext}"
        print("Entered a museo-block")
        directory_path = os.path.dirname(str(select_out.get()))
        museo_filename = str(museo_script_output.get())
        museo_filename = os.path.join(filebase,museo_filename)
        museoscript_parse(output_file_blast,museo_filename,float(similarity_threshold_entry.get()))



def loop_blast():
# run single file
  if os.path.isfile(select_query2.get()):
      file = select_query2.get()

      # Redirect output to the output folder
      filebase = os.path.basename(file)
      output_file = filebase.split('.')[0] + ".out"
      output_file = os.path.join(select_out2.get(),output_file)
      input_file = file
      print("db: ", select_db2.get())
      print("input file: ", input_file)
      # remove gaps and store new sequences into temporary file
      base, ext = os.path.splitext(file)
      temporary_file = base + "_temp" + ext
      remove_gaps(input_file, temporary_file)
      # remove .ext from the db name
      db = str(select_db2.get().rsplit('.', 1)[0])
      b = subprocess.Popen(
          f"{blast_type2.get()} -out {output_file} -query {temporary_file} -outfmt '{int(6)} length pident qseqid sseqid sseq qframe sframe' "
          f"-evalue {evalue2.get()} -db {db} -num_threads {int(threads2.get())}",
          shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

      b.wait()
      # Capture the stdout and stderr
      stdout, stderr = b.communicate()

      # Print the stdout and stderr
      print("BLAST Standard Output:")
      print(stdout.decode('utf-8'))

      print("\nBLAST Standard Error:")
      print(stderr.decode('utf-8'))

      # Check the return code
      return_code = b.returncode
      print(f"\nBLAST Return Code: {return_code}")

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
      os.remove(temporary_file)
      filesplit = filebase.split('.')
      modified_output = str(select_out2.get()) + "/" + filesplit[0] + '_blastmatchesadded.' + filesplit[1]
#      modified_output = filesplit[0] + '_blastmatchesadded.' + filesplit[1]
      print("output file: ", output_file)
      if blast_type2.get() == "blastx":
          db_name = select_db2.get()
          db_name = db_name.split('/')[-1]
          db_name = db_name.rsplit('.',1)[0]
          blastx_parse(input_file, output_file, modified_output, extra_nucleotide_entry.get(),db_name)
      else:
          blast_parse(input_file, output_file, modified_output)
# run in the loop
  else:
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

            print("input file: ", input_file)
            # remove gaps and store new sequences into temporary file
            base, ext = os.path.splitext(file)
            temporary_file =  os.path.join(directory, f"{base}_temp{ext}")
            remove_gaps(input_file,temporary_file)
            b=subprocess.Popen(
                    f"{blast_type2.get()} -out {output_file} -query {temporary_file} -outfmt '{int(6)} length pident qseqid sseqid sseq qframe sframe' "
                    f"-evalue {evalue2.get()} -db {select_db2.get()} -num_threads {int(threads2.get())}",
                    shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            b.wait()
            # Capture the stdout and stderr
            stdout, stderr = b.communicate()

            # Print the stdout and stderr
            print("BLAST Standard Output:")
            print(stdout.decode('utf-8'))

            print("\nBLAST Standard Error:")
            print(stderr.decode('utf-8'))

            # Check the return code
            return_code = b.returncode
            print(f"\nBLAST Return Code: {return_code}")

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
            os.remove(temporary_file)
            filesplit = file.split('.')
            modified_output = filesplit[0] + '_blastmatchesadded.' + filesplit[1]
            modified_output =  os.path.join(str(select_out2.get()),modified_output)
            if blast_type2.get() == "blastx":
                blastx_parse(input_file, output_file, modified_output,extra_nucleotide_entry.get())
            else:
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
    if checkbox == museoscript_checkbox:
        if state == 1:
            blast_typeVar.set('blastn')
            blast_type.config(state="disabled")
        else:
            blast_type.config(state="readonly")

        # Freeze the outfmt and other command when museoscript mode is selected



def create_checkbox(frame, text, row, column, variable, all_frames):
    checkbox = Checkbutton(frame, text=text, bg="#fffacd", onvalue=1, offvalue=0, variable=variable)
    checkbox.grid(row=row, column=column, columnspan=6, sticky="w", padx=(6, 0), pady=1)
    checkbox.var = variable
    checkbox.configure(command=lambda: on_checkbox_click(frame, checkbox, all_frames))
    return checkbox

def restrict_to_blastn(frame, checkbox):
    pass

def create_museoscript_checkbox(frame, text, row, column, variable):
    checkbox = Checkbutton(frame, text=text, bg="#fffacd", onvalue=1, offvalue=0, variable=variable)
    checkbox.grid(row=row, column=column, columnspan=6, sticky="w", padx=(6, 0), pady=1)
    checkbox.var = variable
    checkbox.configure(command=lambda: on_checkbox_click(frame, checkbox, all_frames))
    return checkbox

#def mkdb_window_cmd():
#    make_db()

###GUI part of the program ###
top = Tk()
top.title('BLAST-Align')
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
run_batch_checkbox = create_checkbox(third_frame, "Run BLAST-Align", 0, 0, run_batch_var, main_frames)

build_db_var = IntVar()
run_batch_checkbox3 = create_checkbox(fourth_frame, "Build BLAST database", 0, 0, build_db_var, main_frames)


### Title Frame ###
banner_frame = LabelFrame(top,bg="#f0f0f0")
banner_img = ImageTk.PhotoImage(Image.open("iTaxoTools Digital linneaeus MICROLOGO.png"))


my_image_label = Label(banner_frame, image=banner_img).grid(row=0, column=0, rowspan=3, sticky="nsew")
banner_frame.grid(column=0, row=0,  sticky="nsew")

program_name = Label(banner_frame, text="BLAST-Align",bg="#f0f0f0",font=Font(size=20))
program_name.grid(row=1, column=1)
program_description = Label(banner_frame, text="Add sequences to alignment if matching in Blast search",bg="#f0f0f0")
program_description.grid(row=1, column=2,  sticky="nsew", ipady=4, ipadx=15)

author = Label(banner_frame, text="Code by Nikita Kulikov, Anja-Kristina Schulz and Stefanos Patmanidis \nGUI modified from BLAST-GUI by Du et al. (2020) / https://github.com/byemaxx/BlastGUI",
        font=Font(size=8),bg="#f0f0f0", anchor="w", justify="left")
author.grid(row=2, column=1, columnspan=2)


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
threads.grid(row=4, column=5, sticky="we",padx=(0,10), pady=(10, 0))

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
blast_type = Combobox(second_frame, textvariable=blast_typeVar, values=blast_typeList) #, font=('', 13))
blast_type.grid(row=5, column=5, padx=(0,10), sticky="w")

###############################
### NEW checkbox for museoscript mode
museoscript_mode_var = IntVar()
museoscript_checkbox = create_checkbox(second_frame, "Museoscript mode", 0, 1, museoscript_mode_var,  main_frames)
museoscript_checkbox.configure(command=museoscript_widgets)

### NEW  WIDGET FOR MUSEOSCRIPT MODE ### PLACED HERE BECAUSE BLAST TYPE MUST BE DEFINED
museoscript_parameters = Label(second_frame, text="MUSEOSCRIPT PARAMETERS", bg="#fffacd")
museoscript_parameters.grid_forget()

museo_script_output_text = Label(second_frame, text="Museoscript output filename:", bg="#fffacd")
museo_script_output_text.grid_forget()
museo_script_output = Entry(second_frame, width=40)
#museo_script_output.insert(0, "Entry the name of museoscript output file")

similarity_threshold_label = Label(second_frame, text="Pident:", bg="#fffacd")
similarity_threshold_label.grid_forget()

similarity_threshold_entry = Entry(second_frame, width=25)
similarity_threshold_entry.insert(0, "0.9")
similarity_threshold_entry.grid_forget()

# Initially hide the widget
museo_script_output.grid_forget()
museoscript_widgets()


# Configure style for Combobox. Change method's background to from gray to white
style = Style()
style.configure('TCombobox',
                fieldbackground='white',  # Field background (entry part)
                background='white')      # Background of the dropdown part

# Map different styles for readonly and disabled states
style.map('TCombobox',
          fieldbackground=[('disabled', 'lightgray')],
          background=[('disabled', 'lightgray')],
          foreground=[('disabled', 'gray')],
          )
blast_type.configure(style='TCombobox')
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

button_3d = Button(third_frame, text="Browse input directory\nfor batch processing", width=12, height=2, command=lambda: select_directory("query"))
button_3d.grid(row=3, column=1, sticky="we", padx=(5, 25))

# 4th row

method2 = Label(third_frame, text="Methods:",bg="#fffacd")
method2.grid(row=4, column=0, sticky="e")

blast_typeVar2 = StringVar(value='blastn')
blast_type2 = Combobox(third_frame, textvariable=blast_typeVar2, values=blast_typeList) # , font=('', 13))
blast_type2.grid(row=4, column=1, sticky="we")
# Bind the event to toggle the visibility of extra nucleotide widgets
blast_type2.bind("<<ComboboxSelected>>", switch_nucleotide_widgets)

evalue2 = Label(third_frame, text="E-value:",bg="#fffacd")
evalue2.grid(row=4, column=2, sticky="e", padx=(10,0), pady=(10, 0))

evalue2 = Entry(third_frame, width=25)
evalue2.insert(0, "1e-5")  # Default value
evalue2.grid(row=4, column=3, sticky="we", padx=(0, 5), pady=(10, 0))

threads2 = Label(third_frame, text="Threads:",bg="#fffacd")
threads2.grid(row=4, column=4, sticky="e", padx=(10,0), pady=(10, 0))

threads2 = Entry(third_frame, width=25)
threads2.insert(0, "4")  # Default value
threads2.grid(row=4, column=5, sticky="w", padx=(0,10), pady=(10, 0))

### EXTRA NUCLEOTIDE WIDGET FOR BLASTX METHOD ###
extra_nucleotide_entry = Entry(third_frame, width=40)
extra_nucleotide_entry.insert(0, "Extra nucleotide file for blastx")
extra_nucleotide_browse_button = Button(third_frame, text="Browse", width=8, height=2, command=lambda: select_fadb_button_cmd("extra_nucleotide_file",0))

# Switch function initially to set the visibility of widgets
switch_nucleotide_widgets(None)

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
database_name.grid(row=2, column=5, padx=(0,10), sticky="we")

###### FIFTH FRAME ######

#button_help = Button(fifth_frame, text="Help", bg="#add8e6", width=8, height=2, command=main_instructions)
#button_help.grid(row=0, column=0, columnspan=3, sticky="nsew", padx=(5, 25))


#button_start = Button(fifth_frame, text="Start", bg="#90ee90", width=8, height=2, command=start_processing)
#button_start.grid(row=0, column=4, columnspan=3, sticky="nsew", padx=(5, 25))

button_help = Button(fifth_frame, text="Help", bg="#add8e6", width=8, height=2, command=main_instructions)
button_help.grid(row=0, column=0, columnspan=3, sticky="nsew", padx=(15, 25), pady=10)

button_start = Button(fifth_frame, text="Start", bg="#90ee90", width=8, height=2, command=start_processing)
button_start.grid(row=0, column=4, columnspan=3, sticky="nsew", padx=(15, 25), pady=10)

###############################

##### BUTTONS AND ENTRY FIELDS CONTROL #####

buttons = []
entry_widgets = []


top.mainloop()
