"""
BLACKOUT Confluence Loader - Load Confluence export data
"""

import json
import os
from pathlib import Path
from typing import Any


def load(confluence_export_path: str) -> list[dict[str, Any]]:
    """
    Load Confluence export data.

    Expected structure:
    confluence_export/
        space_name/
            page_id.json or page_id/

    Or flat structure with JSON files.
    """
    records = []
    export_path = Path(confluence_export_path)

    if not export_path.exists():
        print(f"Confluence export path not found: {confluence_export_path}")
        return records

    # Handle both flat and nested structures
    json_files = list(export_path.rglob("*.json"))

    for json_file in json_files:
        try:
            with open(json_file, "r") as f:
                page = json.load(f)

            # Handle different Confluence export formats
            content = page.get("content", page)
            body = content.get("body", {})
            storage = body.get("storage", {})
            text = storage.get("value", "")

            # Extract author info
            author = content.get("author", {})
            author_name = author.get("displayName", author.get("username", ""))

            record = {
                "source_system": "confluence",
                "record_type": "document",
                "id": content.get("id", json_file.stem),
                "author_raw": author_name,
                "timestamp": content.get("lastModifiedDate"),
                "text": text,
                "title": content.get("title", ""),
                "url": content.get("_links", {}).get("base", "") + content.get("_links", {}).get("webui", ""),
                "thread_or_channel": content.get("space", {}).get("key", ""),
            }
            records.append(record)

        except (json.JSONDecodeError, KeyError) as e:
            print(f"Error loading {json_file}: {e}")

    return records
