# scrcpy Optimization Guide for Low-Spec PCs

This PC runs an **Intel Pentium Silver N5000** with integrated **Intel UHD Graphics 605**.
To keep CPU/GPU utilization low and prevent thermal throttling:

## Recommended Command
```powershell
scrcpy --max-size=1024 --video-bit-rate=2M --max-fps=30 --no-audio
```

## Parameter Rationale
| Parameter | Value | Benefit |
| :--- | :--- | :--- |
| `--max-size` | `1024` | Downscales resolution for rapid hardware decoding. |
| `--video-bit-rate`| `2M` | Minimal USB/Wi-Fi bus traffic. |
| `--max-fps` | `30` | Cuts decoder load by 50% compared to default 60 FPS. |
| `--no-audio` | Enabled | Eliminates audio transcoding and latency buffer. |

## Quick Launcher
Run directly:
```powershell
python tools/scrcpy_helper.py
```
