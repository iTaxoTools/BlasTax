### Bundling

Bundling requires PyInstaller and the BLAST+ binaries.
A helper script is included to fetch the latest BLAST+ binaries.

Bundling is best done within a virtual environment, such as with the use of pipenv.

```
pip install -r requirements.txt
python tools/get_blast_binaries.py
pyinstaller blastGUI_test.spec
```

If all goes well, the bundle will be saved in the `dist` folder.

PS. The binary getter can also be used when running the script directly to execute the program without installing BLAST+ on a system level.