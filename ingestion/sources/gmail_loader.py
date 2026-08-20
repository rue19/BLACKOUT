"""
BLACKOUT Gmail Loader - Load Gmail export data
"""

import json
from pathlib import Path
from typing import Any


def load(gmail_export_path: str) -> list[dict[str, Any]]:
    """Load Gmail export data (MBOX or JSON format)."""
    records = []
    export_path = Path(gmail_export_path)

    if not export_path.exists():
        print(f"Gmail export path not found: {gmail_export_path}")
        return records

    for json_file in export_path.rglob("*.json"):
        try:
            with open(json_file, "r") as f:
                email = json.load(f)

            headers = {h["name"]: h["value"] for h in email.get("payload", {}).get("headers", [])}

            record = {
                "source_system": "gmail",
                "record_type": "message",
                "id": email.get("id", json_file.stem),
                "author_raw": headers.get("From", ""),
                "timestamp": email.get("internalDate"),
                "text": email.get("snippet", ""),
                "title": headers.get("Subject", ""),
                "thread_or_channel": email.get("threadId", ""),
            }
            records.append(record)

        except (json.JSONDecodeError, KeyError) as e:
            print(f"Error loading {json_file}: {e}")

    return records
