# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['mastering_tool.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=['scipy', 'scipy.signal', 'pyloudnorm', 'soundfile', 'numpy', 'flask', 'requests', 'threading', 'webbrowser', 'werkzeug', 'jinja2', 'audio_analyzer', 'batch_processor', 'audio_processor', 'config', 'web_server'],
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
    name='AudioMasteringTool',
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
