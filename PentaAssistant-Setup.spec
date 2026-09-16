# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['ui.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[
        'webview',
        'webview.platforms.winforms',
        'webview.platforms.edgechromium',
        # Pillow / PIL - required by desktop_controller.py
        'PIL',
        'PIL.Image',
        'PIL.ImageGrab',
        'PIL.ImageDraw',
        'PIL.ImageFont',
        'PIL._imagingtk',
        # Networking & async
        'websockets',
        'websockets.legacy',
        'websockets.legacy.server',
        'websockets.legacy.client',
        # Screen capture & input (common extras)
        'pyautogui',
        'pynput',
        'pynput.keyboard',
        'pynput.mouse',
        # Windows-specific
        'win32api',
        'win32con',
        'win32gui',
        'win32process',
        'pywintypes',
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
    a.binaries,
    a.datas,
    [],
    name='PentaAssistant-Setup',
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
)
