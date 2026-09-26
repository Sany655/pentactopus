#!/data/data/com.termux/files/usr/bin/bash
# ==============================================================================
# Pentactopus Android Companion Daemon Runner
# ==============================================================================
# Keeps the companion relay persistent in Termux / Android background environment.
# Acquires wake-lock and monitors connectivity to the command hub.
# Automatically cleans up processes, PID locks, and releases wake-lock on exit.

HUB_URL="${1:-http://192.168.1.100:5050}"
DEVICE_ID="${2:-android_phone_$(uname -m)}"
TOKEN="${3:-penta_client_token}"

PID_FILE="/data/data/com.termux/files/usr/tmp/pentactopus_companion.pid"

cleanup() {
    echo ""
    echo "[Cleanup] Stopping Pentactopus Companion cleanly..."
    if [ -f "${PID_FILE}" ]; then
        rm -f "${PID_FILE}"
    fi
    if command -v termux-wake-unlock >/dev/null 2>&1; then
        echo "[Power] Releasing Termux Wake Lock..."
        termux-wake-unlock
    fi
    echo "[Cleanup] All companion resources released cleanly."
    exit 0
}

trap cleanup SIGINT SIGTERM EXIT

echo "================================================="
echo "🐙 Pentactopus Android Companion Daemon"
echo "Target Hub : ${HUB_URL}"
echo "Device ID  : ${DEVICE_ID}"
echo "================================================="

# Acquire Termux Wake Lock to prevent Android OS deep sleep
if command -v termux-wake-lock >/dev/null 2>&1; then
    echo "[Power] Acquiring Termux Wake Lock..."
    termux-wake-lock
fi

# Record runner PID
mkdir -p "$(dirname "${PID_FILE}")"
echo "$$" > "${PID_FILE}"

# Ensure python is available
if ! command -v python >/dev/null 2>&1; then
    echo "[Setup] Python not detected. Installing python via pkg..."
    pkg update -y && pkg install -y python
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RELAY_SCRIPT="${SCRIPT_DIR}/companion_relay.py"

if [ ! -f "${RELAY_SCRIPT}" ]; then
    echo "[Error] companion_relay.py not found in ${SCRIPT_DIR}"
    exit 1
fi

echo "[Daemon] Starting persistent loop. Press Ctrl+C to terminate."

while true; do
    echo "[Daemon] Launching companion relay..."
    python "${RELAY_SCRIPT}" "${HUB_URL}" "${DEVICE_ID}" "${TOKEN}" &
    CHILD_PID=$!
    wait ${CHILD_PID}
    EXIT_CODE=$?
    echo "[Daemon] Relay exited with code ${EXIT_CODE}. Restarting in 5 seconds..."
    sleep 5
done
