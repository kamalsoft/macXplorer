# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['macXplorer.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('assets/macXplorer.png', 'assets'),
    ],
    hiddenimports=[
        'plugins.diff_plugin',
        'plugins.preview_plugin',
        'plugins.settings_plugin',
        'plugins.terminal_plugin',
        'plugins.workspace_plugin',
    ],
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
    [],
    exclude_binaries=True,
    name='macXplorer',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    icon='assets/macXplorer.icns',
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
    name='macXplorer',
)
app = BUNDLE(
    coll,
    name='macXplorer.app',
    icon='assets/macXplorer.icns',
    bundle_identifier=None,
)
