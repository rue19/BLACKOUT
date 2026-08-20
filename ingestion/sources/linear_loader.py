"""
BLACKOUT Linear Loader - Load Linear export data
"""

import json
from pathlib import Path
from typing import Any


def load(linear_export_path: str) -> list[dict[str, Any]]:
    """Load Linear export data."""
    records = []
    export_path = Path(linear_export_path)

    if not export_path.exists():
        print(f"Linear export path not found: {linear_export_path}")
        return records

    for json_file in export_path.rglob("*.json"):
        try:
            with open(json_file, "r") as f:
                issue = json.load(f)

            record = {
                "source_system": "linear",
                "record_type": "ticket",
                "id": f"linear-{issue.get('id', json_file.stem)}",
                "author_raw": issue.get("assignee", {}).get("name", ""),
                "timestamp": issue.get("createdAt"),
                "text": f"{issue.get('title', '')}\n\n{issue.get('description', '')}",
                "title": issue.get("title", ""),
                "thread_or_channel": issue.get("team", {}).get("name", ""),
                "status": issue.get("state", {}).get("name", ""),
            }
            records.append(record)

        except (json.JSONDecodeError, KeyError) as e:
            print(f"Error loading {json_file}: {e}")

    return records
