"""
BLACKOUT Fireflies Loader - Load Fireflies transcript data
"""

import json
from pathlib import Path
from typing import Any


def load(fireflies_export_path: str) -> list[dict[str, Any]]:
    """Load Fireflies transcript data."""
    records = []
    export_path = Path(fireflies_export_path)

    if not export_path.exists():
        print(f"Fireflies export path not found: {fireflies_export_path}")
        return records

    for json_file in export_path.rglob("*.json"):
        try:
            with open(json_file, "r") as f:
                transcript = json.load(f)

            record = {
                "source_system": "fireflies",
                "record_type": "message",
                "id": f"fireflies-{transcript.get('id', json_file.stem)}",
                "author_raw": transcript.get("host", ""),
                "timestamp": transcript.get("date"),
                "text": transcript.get("transcript", ""),
                "title": transcript.get("title", ""),
                "thread_or_channel": transcript.get("meeting_id", ""),
            }
            records.append(record)

        except (json.JSONDecodeError, KeyError) as e:
            print(f"Error loading {json_file}: {e}")

    return records
