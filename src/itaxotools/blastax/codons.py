# This code is part of the Biopython distribution and governed by its
# license.  Please see the LICENSE file that should have been included
# as part of this package.
# It was modified for use in BlasTax.
# Here we are only interested in the id and name.

"""Helper script to update Codon tables from the NCBI.

These tables are based on parsing the NCBI file:
ftp://ftp.ncbi.nih.gov/entrez/misc/data/gc.prt
"""

import re

from itaxotools.blastax import resources


def line_wrap(text, indent=0, max_len=78, string=False):
    """Return a wrapped line if length is larger max_len.

    The new parameter 'string' allows to wrap quoted text which is delimited
    by single quotes. It adds a closing quote to the end of the line and an
    opening quote to the start of the next line.
    """
    split_len = max_len if not string else max_len - 2
    if len(text) <= max_len:
        return text
    line = text[:split_len]
    assert " " in line, line
    line, rest = line.rsplit(" ", 1)
    # New:
    if string:
        line += ' "'
        rest = '"' + rest
    rest = " " * indent + rest + text[split_len:]
    assert len(line) < max_len
    if indent + len(rest) <= max_len:
        return line + "\n" + rest
    else:
        return line + "\n" + line_wrap(rest, indent, max_len, string)


def get_codon_tables() -> tuple[str, dict[int, str]]:
    genetic_codes = resources.documents.gc.resource
    version = ""
    tables: dict[int, str] = {}
    for line in genetic_codes:
        if not version and line.startswith("--  Version"):
            version = line.split("Version", 1)[1].strip()
        if line[:2] == " {":
            names = []
            id = None
            aa = None
            start = None
            bases = []
        elif line[:6] == "  name":
            names.append(re.search('"([^"]*)"', line).group(1))
        elif line[:8] == "    name":
            names.append(re.search('"(.*)$', line).group(1))
        elif line == ' Mitochondrial; Mycoplasma; Spiroplasma" ,\n':
            names[-1] = names[-1] + " Mitochondrial; Mycoplasma; Spiroplasma"
        elif line[:4] == "  id":
            id = int(re.search(r"(\d+)", line).group(1))
        elif line[:10] == "  ncbieaa ":
            aa = line[12 : 12 + 64]
        elif line[:10] == "  sncbieaa":
            start = line[12 : 12 + 64]
        elif line[:9] == "  -- Base":
            bases.append(line[12 : 12 + 64])
        elif line[:2] == " }":
            assert names != [] and id is not None and aa is not None
            assert start is not None and bases != []
            if len(names) == 1:
                names.append(None)
            tables[id] = names[0]
        elif line[:2] == "--" or line in ("\n", "}\n", "Genetic-code-table ::= {\n"):
            pass
        else:
            raise Exception("Unparsed: " + repr(line))

    return version, tables


if __name__ == "__main__":
    version, tables = get_codon_tables()
    print("VERSION:", version)
    for id, name in tables.items():
        print(f"{(str(id) + ':').rjust(3)} {name}")
