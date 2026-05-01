# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec file for Pacman."""

import sys
import os
from pathlib import Path

block_cipher = None

project_root = Path(SPECPATH)

# Ensure config.json exists before packaging
config_file = project_root / "config.json"
if not config_file.exists():
    raise RuntimeError(
        f"config.json not found at {config_file}. "
        "A config.json file must be present at the project root to package."
    )

# Collect all assets and instructions
datas = [
    (str(config_file), "."),
    (str(project_root / "instructions.txt"), "."),
    (str(project_root / "assets"), "assets"),
]

# Locate libmlx.so from the mlx package
import importlib.util
mlx_spec = importlib.util.find_spec("mlx")
mlx_pkg_dir = str(Path(mlx_spec.origin).parent) if mlx_spec else ""
mlx_lib = os.path.join(mlx_pkg_dir, "libmlx.so")
if os.path.exists(mlx_lib):
    binaries = [(mlx_lib, "mlx")]
else:
    binaries = []

a = Analysis(
    ["pac-man.py"],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=[
        "mazegenerator",
        "mazegenerator.mazegenerator",
        "pydantic",
        "pydantic_core",
        "mlx",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="pacman",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    console=True,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="pacman",
)
