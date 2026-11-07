# -*- mode: python ; coding: utf-8 -*-

import sys
import os
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None

# Collect all assets and CustomTkinter theme / font files
datas = [
    ('assets', 'assets'),
]
datas += collect_data_files('customtkinter')

hiddenimports = [
    'customtkinter',
    'darkdetect',
    'PIL',
    'PIL.Image',
    'google',
    'google.genai',
    'google.genai.types',
    'src',
    'src.config',
    'src.app',
    'src.utils.file_helper',
    'src.utils.gemini_helper',
    'src.utils.exporter',
    'src.agents.base_agent',
    'src.agents.triage_agent',
    'src.agents.logic_agent',
    'src.agents.forensic_agent',
    'src.agents.stress_agent',
    'src.agents.synthesizer_agent',
    'src.agents.orchestrator',
    'src.ui.theme',
    'src.ui.header',
    'src.ui.input_panel',
    'src.ui.agent_telemetry',
    'src.ui.dossier_view',
    'src.ui.history_view',
]
hiddenimports += collect_submodules('customtkinter')

a = Analysis(
    ['main.py'],
    pathex=['.'],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
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
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='DevDiagnosis',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/app_icon.ico',
)
