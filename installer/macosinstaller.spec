# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['scripts/run_app.py'],
             pathex=['/Users/amaro/simtravel'],
             binaries=[],
	     datas=[('build/lib/', '.'), ('img', './img/')],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=['tkinter'],
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
          name='SIMTRAVEL',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
	  console=False,
	  windowed=True,
	  icon='img/icon.ico' )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='SIMTRAVEL macos')
app = BUNDLE(exe,
             name='SIMTRAVEL.app',
             icon='img/icon.icns',
             bundle_identifier=None,
	     info_plist={
            		'NSPrincipalClass': 'NSApplication',
            		'NSAppleScriptEnabled': False,
            		'CFBundleDocumentTypes': [
                		{
                    			'CFBundleTypeName': 'My File Format',
                    			'CFBundleTypeIconFile': 'MyFileIcon.icns',
                    			'LSItemContentTypes': ['com.example.myformat'],
                    			'LSHandlerRank': 'Owner'
                    		}]
            },
	     )
