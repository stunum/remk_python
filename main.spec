# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_dynamic_libs
from PyInstaller.building.datastruct import Tree
from PyInstaller.building.build_main import Analysis, PYZ, EXE

binaries = collect_dynamic_libs('ai')
# Tree 返回 (src, dest, type)，需要取前两项
ai_tree = [(src, dest) for src, dest, _type in Tree('ai', prefix='ai') if not src.endswith(".py")]
a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=binaries,
    datas=ai_tree,
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