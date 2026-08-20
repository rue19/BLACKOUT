"""
BLACKOUT Jira Loader - Load Jira export data
"""

import json
from pathlib import Path
from typing import Any


def load(jira_export_path: str) -> list[dict[str, Any]]:
    """Load Jira export data."""
    records = []
    export_path = Path(jira_export_path)

    if not export_path.exists():
        print(f"Jira export path not found: {jira_export_path}")
        return records

    for json_file in export_path.rglob("*.json"):
        try:
            with open(json_file, "r") as f:
                issue = json.load(f)

            fields = issue.get("fields", {})

            record = {
                "source_system": "jira",
                "record_type": "ticket",
                "id": f"jira-{issue.get('key', json_file.stem)}",
                "author_raw": fields.get("assignee", {}).get("displayName", ""),
                "timestamp": fields.get("created"),
                "text": f"{fields.get('summary', '')}\n\n{fields.get('description', '')}",
                "title": fields.get("summary", ""),
                "thread_or_channel": fields.get("project", {}).get("key", ""),
                "status": fields.get("status", {}).get("name", ""),
            }
            records.append(record)

        except (json.JSONDecodeError, KeyError) as e:
            print(f"Error loading {json_file}: {e}")

    return records
