"""
BLACKOUT HubSpot Loader - Load HubSpot export data
"""

import json
from pathlib import Path
from typing import Any


def load(hubspot_export_path: str) -> list[dict[str, Any]]:
    """Load HubSpot export data (deals, contacts, etc.)."""
    records = []
    export_path = Path(hubspot_export_path)

    if not export_path.exists():
        print(f"HubSpot export path not found: {hubspot_export_path}")
        return records

    for json_file in export_path.rglob("*.json"):
        try:
            with open(json_file, "r") as f:
                deal = json.load(f)

            properties = deal.get("properties", {})

            record = {
                "source_system": "hubspot",
                "record_type": "deal",
                "id": f"hubspot-{deal.get('id', json_file.stem)}",
                "author_raw": properties.get("hubspot_owner_id", ""),
                "timestamp": properties.get("createdate"),
                "text": f"Deal: {properties.get('dealname', '')}\nStage: {properties.get('dealstage', '')}\nAmount: {properties.get('amount', '')}",
                "title": properties.get("dealname", ""),
                "thread_or_channel": properties.get("pipeline", ""),
                "stage": properties.get("dealstage", ""),
            }
            records.append(record)

        except (json.JSONDecodeError, KeyError) as e:
            print(f"Error loading {json_file}: {e}")

    return records
