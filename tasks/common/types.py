from enum import Enum


class BlastMethod(Enum):
    blastn = ("blastn", "Nucleotide-Nucleotide")
    blastp = ("blastp", "Protein-Protein")
    blastx = ("blastx", "Translated Query-Protein Subject")
    tblastn = ("tblastn", "Protein Query-Translated Subject")
    tblastx = ("tblastx", "Translated Query-Translated Subject")

    def __init__(self, executable: str, description: str):
        self.executable = executable
        self.description = description
        self.label = f"{str(executable+":").ljust(10)} {description.lower().replace("-", " - ")}"
