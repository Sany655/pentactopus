from __future__ import annotations

import argparse
from pathlib import Path

from .agent import WindowsAgent
from .policy import load_policy


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Open Notepad and type a local unsent draft for review."
    )
    parser.add_argument(
        "--policy",
        type=Path,
        default=Path(__file__).with_name("policy.example.json"),
        help="Path to the local Windows agent policy JSON file",
    )
    args = parser.parse_args()
    text = input("Text to type into Notepad: ")

    agent = WindowsAgent(policy=load_policy(args.policy))
    result = agent.run_task(
        {
            "capability": "draft_text_in_notepad",
            "tier": 3,
            "text": text,
        }
    )
    print(
        f"Opened {result['result']['app']} and typed "
        f"{result['result']['character_count']} characters. Review in Notepad; "
        "nothing was sent or saved."
    )


if __name__ == "__main__":
    main()
