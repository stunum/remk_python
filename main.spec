# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_dynamic_libs
from PyInstaller.building.datastruct import Tree
from PyInstaller.building.build_main import Analysis, PYZ, EXE

binaries = collect_dynamic_libs('ai')

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=binaries,
    datas=[Tree('ai', prefix='ai')],
    hiddenimports=['uvicorn', 'fastapi', 'onnxruntime', 'sklearn', 'scipy.signal'],
    hookspath=[],
    runtime_hooks=[],
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
    console=True,
)