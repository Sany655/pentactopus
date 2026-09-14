# USB Debugging & Physical Phone Setup Guide

To control an Android device with this AI agent:

## Step 1: Enable Developer Options
1. Open **Settings** on your Android phone.
2. Go to **About Phone** (or **System > About Phone**).
3. Tap **Build Number** 7 times until you see the message: *"You are now a developer!"*.

## Step 2: Enable USB Debugging
1. Go back to **Settings > System > Developer options** (or **Additional settings > Developer options**).
2. Toggle on **USB debugging**.
3. *Special Vendor Requirements:*
   - **Xiaomi / Redmi / POCO (MIUI / HyperOS):** Also enable **"USB debugging (Security settings)"** to allow input simulation (tap/type).
   - **OPPO / Realme (ColorOS):** Toggle **"Disable permission monitoring"**.
   - **Vivo (Funtouch OS):** Enable **"USB simulated input"**.

## Step 3: Connect to Windows PC
1. Connect phone with a USB data cable.
2. When prompted on the phone with **"Allow USB debugging?"**, check **"Always allow from this computer"** and tap **Allow**.

## Step 4: Verify via Terminal
Run in PowerShell:
```powershell
adb devices -l
```
You should see:
```text
List of devices attached
<device-serial>    device product:... model:... device:...
```
If it says `unauthorized`, unlock your phone and accept the prompt.
