"""Main entry point for AI-Android-Agent."""

import argparse
import sys
import os
from agent.core import AndroidAgent
from adb.client import ADBClient
from models.router import get_model_provider, PROVIDER_REGISTRY

try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))
except ImportError:
    pass

def main():
    parser = argparse.ArgumentParser(description="Android Computer-Use AI Agent")
    parser.add_argument("--goal", type=str, default="Open Android Settings", help="Goal for the agent to accomplish")
    parser.add_argument(
        "--provider",
        type=str,
        choices=list(PROVIDER_REGISTRY.keys()),
        default="gemini",
        help="Model provider (gemini, openai, anthropic, deepseek, groq, openrouter, ollama, mock)"
    )
    parser.add_argument("--model", type=str, default=None, help="Specific model name")
    parser.add_argument("--dry-run", action="store_true", help="Simulate without real device ADB execution")
    parser.add_argument("--serial", type=str, default=None, help="Target device ADB serial")
    args = parser.parse_args()

    print("="*60)
    print("      ANDROID COMPUTER-USE AI AGENT (LIGHTWEIGHT)      ")
    print("="*60)

    # Initialize model provider via unified gateway
    model = get_model_provider(args.provider, model_name=args.model)

    adb = ADBClient(device_serial=args.serial)

    # Check connected devices
    if not args.dry_run:
        try:
            devices = adb.get_devices()
            print(f"[ADB] Connected devices: {len(devices)}")
            for d in devices:
                print(f"  - {d['serial']} ({d['state']})")
            if not devices:
                print("[WARN] No physical Android device connected via ADB. Switching to dry-run mode for safety.")
                args.dry_run = True
        except Exception as e:
            print(f"[WARN] ADB check failed: {e}. Switching to dry-run mode.")
            args.dry_run = True

    agent = AndroidAgent(model_provider=model, adb_client=adb, dry_run=args.dry_run)
    result = agent.run_goal(args.goal)

    print("\n" + "="*60)
    print(f"EXECUTION RESULT: {'SUCCESS' if result.get('success') else 'FAILED'}")
    print(f"Details: {result}")
    print("="*60)

    sys.exit(0 if result.get("success") else 1)

if __name__ == "__main__":
    main()
