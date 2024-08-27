# -*- mode: python ; coding: utf-8 -*-

from os import environ

NAME = environ.get('APP_NAME', None)
FILENAME = environ.get('APP_FILENAME', None)
ICON = environ.get('APP_ICON_ICO', None)
SCRIPT = environ.get('APP_SCRIPT', None)


block_cipher = None

# Could also use pyinstaller's Entrypoint()
a = Analysis([SCRIPT],
             pathex=[],
             binaries=[('../../bin', 'bin')],
             datas=[
                 ('../../documents', 'documents'),
                 ('../../graphics', 'graphics'),
                 ('../../logos', 'logos'),
                 ('../../core.py', '.'),
                 ('../../utils.py', '.'),
                 ('../../tasks', 'tasks'),
             ],
             hiddenimports=[],
             hookspath=[],
             hooksconfig={},
             runtime_hooks=[],
             excludes=[
                'matplotlib',
                'PIL',
                'pandas',
            ],
             noarchive=False)
pyz = PYZ(a.pure)

exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.datas,
          [],
          name=FILENAME,
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=False,
          disable_windowed_traceback=False,
          argv_emulation=False,
          target_arch=None,
          codesign_identity=None,
          entitlements_file=None,
          icon=ICON)
