import os
import sys
import time
import threading

# Add current directory to path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from ui import run_server
from penta.penta_daemon import PentaDaemon

if __name__ == "__main__":
    print("Starting Pentactopus Sidecar Daemon...")
    
    # 1. Start HTTP Dashboard Server on port 5050
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    
    # 2. Start Background Device Daemon
    try:
        cloud_url = os.environ.get("PENTA_CLOUD_URL", "http://localhost:5051")
        penta_daemon = PentaDaemon(cloud_url=cloud_url)
        penta_daemon.start()
        print(f"PentaDaemon active & paired with {cloud_url}")
    except Exception as e:
        print(f"Daemon start error: {e}")
    
    # Keep main thread alive
    try:
        while True:
            time.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        pass
