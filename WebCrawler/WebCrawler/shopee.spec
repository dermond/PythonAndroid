# -*- mode: python ; coding: utf-8 -*-


block_cipher = None


a = Analysis(
    ['D:\\GitHub\\PythonAndroid\\WebCrawler\\WebCrawler\\shopee.py'],
    pathex=[],
    binaries=[],
    datas=[('D:\\GitHub\\PythonAndroid\\WebCrawler\\WebCrawler\\env\\Lib\\site-packages\\cv2\\*', 'cv2')],
    hiddenimports=['ppadb','ddddocr','cv2'],  # 添加這一行
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='shopee',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='shopee',
)
