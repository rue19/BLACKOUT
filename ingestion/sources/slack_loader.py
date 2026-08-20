"""
BLACKOUT Slack Loader - Load Slack export data
"""

import json
import os
from pathlib import Path
from typing import Any


def load(slack_export_path: str) -> list[dict[str, Any]]:
    """
    Load Slack export data from a directory structure.

    Expected structure:
    slack_export/
        channel_name/
            messages.json

    Returns normalized records.
    """
    records = []
    export_path = Path(slack_export_path)

    if not export_path.exists():
        print(f"Slack export path not found: {slack_export_path}")
        return records

    for channel_dir in export_path.iterdir():
        if not channel_dir.is_dir():
            continue

        channel_name = channel_dir.name
        messages_file = channel_dir / "messages.json"

        if not messages_file.exists():
            continue

        try:
            with open(messages_file, "r") as f:
                messages = json.load(f)

            for msg in messages:
                # Skip bot messages and system messages
                if msg.get("subtype") in ("bot_message", "channel_join", "channel_leave"):
                    continue

                record = {
                    "source_system": "slack",
                    "record_type": "message",
                    "id": msg.get("id", msg.get("ts", "")),
                    "author_raw": msg.get("user", ""),
                    "timestamp": msg.get("ts"),
                    "text": msg.get("text", ""),
                    "thread_or_channel": channel_name,
                }
                records.append(record)

        except (json.JSONDecodeError, KeyError) as e:
            print(f"Error loading {messages_file}: {e}")

    return records
