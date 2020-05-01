# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['scripts\\run_app.py'],
             pathex=['C:\\Users\\Amaro\\OneDrive - UNIVERSIDAD DE SEVILLA\\simtravel'],
             binaries=[],
             datas=[('build/lib/', '.'), ('img', './img/')],
             hiddenimports=[],
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
          name='run_app',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=True,
          icon='img/icon.ico',
           )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='run_app')
