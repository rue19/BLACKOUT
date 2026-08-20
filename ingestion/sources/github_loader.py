"""
BLACKOUT GitHub Loader - Load GitHub export data (PRs, commits, issues)
"""

import json
import os
from pathlib import Path
from typing import Any


def load(github_export_path: str) -> list[dict[str, Any]]:
    """
    Load GitHub export data.

    Expected structure:
    github_export/
        pull_requests.json
        commits.json
        issues.json

    Or API response format.
    """
    records = []
    export_path = Path(github_export_path)

    if not export_path.exists():
        print(f"GitHub export path not found: {github_export_path}")
        return records

    # Load pull requests
    pr_file = export_path / "pull_requests.json"
    if pr_file.exists():
        try:
            with open(pr_file, "r") as f:
                prs = json.load(f)

            for pr in prs:
                record = {
                    "source_system": "github",
                    "record_type": "pull_request",
                    "id": f"pr-{pr.get('id', pr.get('number', ''))}",
                    "author_raw": pr.get("user", {}).get("login", ""),
                    "timestamp": pr.get("created_at"),
                    "text": f"PR #{pr.get('number')}: {pr.get('title', '')}\n\n{pr.get('body', '')}",
                    "title": pr.get("title", ""),
                    "thread_or_channel": pr.get("repository", ""),
                    "merged_at": pr.get("merged_at"),
                    "status": "merged" if pr.get("merged_at") else "open",
                }
                records.append(record)

        except (json.JSONDecodeError, KeyError) as e:
            print(f"Error loading {pr_file}: {e}")

    # Load commits
    commits_file = export_path / "commits.json"
    if commits_file.exists():
        try:
            with open(commits_file, "r") as f:
                commits = json.load(f)

            for commit in commits:
                record = {
                    "source_system": "github",
                    "record_type": "commit",
                    "id": f"commit-{commit.get('sha', '')[:8]}",
                    "author_raw": commit.get("author", {}).get("login", commit.get("commit", {}).get("author", {}).get("name", "")),
                    "timestamp": commit.get("commit", {}).get("author", {}).get("date"),
                    "text": commit.get("commit", {}).get("message", ""),
                    "title": commit.get("commit", {}).get("message", "").split("\n")[0],
                    "thread_or_channel": commit.get("repository", ""),
                }
                records.append(record)

        except (json.JSONDecodeError, KeyError) as e:
            print(f"Error loading {commits_file}: {e}")

    return records
