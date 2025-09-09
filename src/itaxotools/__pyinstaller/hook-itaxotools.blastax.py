from PyInstaller.utils.hooks import collect_data_files, collect_submodules

datas = collect_data_files("itaxotools.blastax")

datas += collect_data_files("Bio.Align")
datas += collect_data_files("Bio.Phylo")

hiddenimports = collect_submodules("itaxotools.blastax.tasks", filter=lambda name: True)
hiddenimports += ["cutadapt._match_tables"]
