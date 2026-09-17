param (
    [string]$Target = "x86_64-pc-windows-msvc"
)

Write-Host "Building Penta Daemon Python sidecar for Tauri..."
Write-Host "Target Architecture: $Target"

# Install all required packages before bundling
python -m pip install pyinstaller pillow websockets pyautogui pynput

# Build the daemon as a single executable
# We use --noconsole to hide the terminal window when it runs in the background
# We name it penta_daemon so the output is penta_daemon.exe
python -m PyInstaller --onefile --noconsole --name penta_daemon `
    --hidden-import PIL `
    --hidden-import PIL.Image `
    --hidden-import PIL.ImageGrab `
    --hidden-import PIL.ImageDraw `
    --hidden-import PIL.ImageFont `
    --hidden-import PIL._imagingtk `
    --hidden-import websockets `
    --hidden-import websockets.legacy `
    --hidden-import websockets.legacy.server `
    --hidden-import websockets.legacy.client `
    --hidden-import asyncio `
    --collect-all PIL `
    run_sidecar.py

if (-not (Test-Path "dist\penta_daemon.exe")) {
    Write-Error "PyInstaller failed to build penta_daemon.exe"
    exit 1
}

# Tauri sidecar naming convention: <name>-<target>
$SidecarName = "penta_daemon-$Target.exe"
$DestDir = "penta-app\src-tauri\binaries"

if (-not (Test-Path $DestDir)) {
    New-Item -ItemType Directory -Path $DestDir | Out-Null
}

$DestPath = Join-Path $DestDir $SidecarName

Write-Host "Moving binary to $DestPath"
Move-Item -Path "dist\penta_daemon.exe" -Destination $DestPath -Force

Write-Host "Sidecar build complete! Cleaning up..."
Remove-Item -Recurse -Force "build" -ErrorAction SilentlyContinue
Remove-Item -Force "penta_daemon.spec" -ErrorAction SilentlyContinue

Write-Host "Done!"
