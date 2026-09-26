#!/data/data/com.termux/files/usr/bin/bash
# ==============================================================================
# Pentactopus Android Companion Daemon Stopper & Cleanup
# ==============================================================================
# Gracefully kills all running companion relay and runner processes, releases
# any held wake-locks, and purges all temporary and cache files from Android.

echo "================================================="
echo "🛑 Stopping Pentactopus Android Companion Daemon"
echo "================================================="

PID_FILE="/data/data/com.termux/files/usr/tmp/pentactopus_companion.pid"

# 1. Kill recorded runner process if active
if [ -f "${PID_FILE}" ]; then
    PID=$(cat "${PID_FILE}")
    if [ -n "${PID}" ] && kill -0 "${PID}" 2>/dev/null; then
        echo "[Daemon] Stopping daemon process PID ${PID}..."
        kill -TERM "${PID}" 2>/dev/null
        sleep 1
        kill -9 "${PID}" 2>/dev/null
    fi
    rm -f "${PID_FILE}"
fi

# 2. Terminate any orphan companion_relay.py processes
pkill -f "companion_relay.py" 2>/dev/null
pkill -f "run_companion.sh" 2>/dev/null

# 3. Release any Termux wake locks
if command -v termux-wake-unlock >/dev/null 2>&1; then
    echo "[Power] Releasing Termux Wake Lock..."
    termux-wake-unlock
fi

# 4. Clean up any temporary sockets or scratch screens
rm -f /data/data/com.termux/files/usr/tmp/penta_* 2>/dev/null
rm -f /sdcard/penta_temp_* 2>/dev/null

echo "--> Pentactopus Companion cleanly stopped. Zero residue remaining."
