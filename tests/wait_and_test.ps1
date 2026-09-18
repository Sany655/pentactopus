param (
    [string]$Version = "v1.0.1",
    [int]$TimeoutMinutes = 15
)

$RepoUrl = "https://github.com/Sany655/pentactopus-releases/raw/main/PentaAssistant-Setup-${Version}.exe"
$DownloadPath = "$env:TEMP\PentaAssistant-Setup-${Version}.exe"
$StartTime = Get-Date

Write-Host "Waiting for release binary at $RepoUrl..."

while ($true) {
    if ((Get-Date) -gt $StartTime.AddMinutes($TimeoutMinutes)) {
        Write-Error "Timed out waiting for the release."
        exit 1
    }

    try {
        $response = Invoke-WebRequest -Uri $RepoUrl -Method Head -UseBasicParsing -ErrorAction Stop
        if ($response.StatusCode -eq 200) {
            Write-Host "Binary found! Downloading..."
            Invoke-WebRequest -Uri $RepoUrl -OutFile $DownloadPath -UseBasicParsing
            break
        }
    } catch {
        Write-Host "Not ready yet. Retrying in 30 seconds..."
        Start-Sleep -Seconds 30
    }
}

Write-Host "Download complete. Installing..."
# Tauri NSIS installers use /S for silent install
Start-Process -FilePath $DownloadPath -ArgumentList "/S" -Wait -NoNewWindow

Write-Host "Installation complete. Running UI tests..."
cd C:\All\works\pentactopus
pytest tests/test_native_tauri_ui.py -v -s

Write-Host "Finished successfully!"
