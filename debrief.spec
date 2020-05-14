# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

added_files = [
    ( '.\*.ui', '.' ),
    ( '.\*.png', '.' ),
    ( '.\*.ico', '.'),
    ( '.\*.json', '.'),
    ( '.\pyqtspinner', 'pyqtspinner' ),
    ( '.\output', 'output' ),
    ( '.\geomag', 'geomag' ),
    ( '.\*.xlsx', '.' ),
]

a = Analysis(['debrief.spec'],
             pathex=['P:\\Python\\bidds-debrief'],
             binaries=[],
             datas=added_files,
             hiddenimports=['openpyxl','PyQt5.uic','timeit','utils','msnparse','pyproj.datadir','json','subprocess','pynmea2'],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='debrief',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=False ,
          icon="patch.ico")
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='debrief')
