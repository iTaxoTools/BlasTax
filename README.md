### Manual bundling

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


### GitHub automation

Compilation of the Windows bundle is done automatically on the GitHub cloud on every push. Since this is a private repository, monthly usage limits apply.

To see the latest build, go to the [Windows action](https://github.com/iTaxoTools/BLAST-Align/actions/workflows/windows.yml), click on the most recent workflow run, then click on the artifact named `itaxotools-blast-gui-test-windows` to download a zip file containing the unsigned executable.
