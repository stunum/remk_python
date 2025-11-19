# -*- mode: python ; coding: utf-8 -*-

# PyInstaller -F main.py --add-data "ai/*.pkl;ai" --add-data "ai/*.onnx;ai" --add-data "ai/*.pyd;ai"  --hidden-import "uvicorn"  --hidden-import "fastapi" --hidden-import onnxruntime --hidden-import sklearn  --hidden-import scipy.signal
a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[('ai/*.pyd', 'ai'),('ai/*.onnx', 'ai'),('ai/*.pkl', 'ai')],
    hiddenimports=['uvicorn', 'fastapi', 'onnxruntime', 'sklearn', 'scipy.signal'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=True,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='main',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
