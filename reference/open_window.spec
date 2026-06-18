# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['open_window.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=["page_main","content_data_center","content_Everyday_Account",
    "content_kehu_center","page_show_all_data","page_denglu"],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='记账簿',
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
    icon=['D://python//bookkeeping//_internal//use_resource//photo//tubiao.ico'],
)
