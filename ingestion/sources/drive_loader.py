"""
BLACKOUT Drive Loader - Load Google Drive export data
"""

import json
from pathlib import Path
from typing import Any


def load(drive_export_path: str) -> list[dict[str, Any]]:
    """Load Google Drive export data."""
    records = []
    export_path = Path(drive_export_path)

    if not export_path.exists():
        print(f"Drive export path not found: {drive_export_path}")
        return records

    for json_file in export_path.rglob("*.json"):
        try:
            with open(json_file, "r") as f:
                doc = json.load(f)

            record = {
                "source_system": "drive",
                "record_type": "document",
                "id": f"drive-{doc.get('id', json_file.stem)}",
                "author_raw": doc.get("owners", [{}])[0].get("displayName", ""),
                "timestamp": doc.get("modifiedTime"),
                "text": doc.get("description", doc.get("name", "")),
                "title": doc.get("name", ""),
                "url": doc.get("webViewLink", ""),
                "thread_or_channel": doc.get("parents", [""])[0] if doc.get("parents") else "",
            }
            records.append(record)

        except (json.JSONDecodeError, KeyError) as e:
            print(f"Error loading {json_file}: {e}")

    return records
