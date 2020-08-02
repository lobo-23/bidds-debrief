# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

added_files = [
    ( '.\*.ui', '.' ),
    ( '.\*.pdf', '.' ),
    ( '.\*.ico', '.'),
    ( '.\SetupBIDDSv4.exe', '.'),
    ( '.\License.txt', '.'),
    ( '.\wpncodes.csv', '.'),
    ( '.\*.json', '.'),
    ( '.\pyqtspinner', 'pyqtspinner' ),
    ( '.\geomag', 'geomag' ),
    ( '.\*.xlsx', '.' ),
]

a = Analysis(['debrief.spec'],
             pathex=['C:\\Users\\Lobo\\Documents\\Python\\bidds-debrief'],
             binaries=[],
             datas=added_files,
             hiddenimports=['openpyxl','PyQt5.uic','timeit','utils','msnparse','pyproj.datadir','json','subprocess','pynmea2','csv','xlrd','resource','pathlib'],
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
          debug=True,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=True ,
          icon="patch.ico")
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='debrief')
