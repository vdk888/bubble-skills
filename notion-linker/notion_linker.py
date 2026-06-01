#!/usr/bin/env python3
"""
Notion Project Linker — Automated content linking for Bubble projects
Updates Notion project pages with new content links (articles, posts, etc.)
"""
import os
import sys
import json
import requests
from datetime import datetime, timezone, timedelta

NOTION_KEY = os.environ.get("NOTION_API_KEY", "")
NOTION_VERSION = "2022-06-28"

# Tracker DBs
SUBSTACK_TRACKER_DB = os.environ.get("SUBSTACK_TRACKER_DB", "")
LINKEDIN_TRACKER_DB = os.environ.get("LINKEDIN_TRACKER_DB", "")

# Project pages (where Notes are written)
SUBSTACK_PROJECT_ID = os.environ.get("SUBSTACK_PROJECT_ID", "")
LINKEDIN_PROJECT_ID = os.environ.get("LINKEDIN_PROJECT_ID", "")


def _headers():
    return {
        "Authorization": f"Bearer {NOTION_KEY}",
        "Notion-Version": NOTION_VERSION,
        "Content-Type": "application/json"
    }


def _get_notes(project_id: str) -> str:
    """Fetch current Notes text from a project page."""
    resp = requests.get(f"https://api.notion.com/v1/pages/{project_id}", headers=_headers())
    if resp.status_code != 200:
        print(f"ERROR: Could not fetch project {project_id}: {resp.text}")
        return ""
    data = resp.json()
    notes = ""
    notes_prop = data.get("properties", {}).get("Notes", {})
    for text_obj in notes_prop.get("rich_text", []):
        notes += text_obj.get("text", {}).get("content", "")
    return notes


def _write_notes(project_id: str, notes: str) -> bool:
    """Write Notes to a project page (overwrites)."""
    chunks = []
    max_len = 2000
    text = notes
    while text:
        chunks.append({"text": {"content": text[:max_len]}})
        text = text[max_len:]
    payload = {"properties": {"Notes": {"rich_text": chunks}}}
    resp = requests.patch(f"https://api.notion.com/v1/pages/{project_id}", headers=_headers(), json=payload)
    if resp.status_code == 200:
        return True
    print(f"ERROR: Failed to update project {project_id}: {resp.text}")
    return False


def update_project_notes(project_id: str, content_line: str) -> bool:
    """
    Append a content line to a project's Notes field — with deduplication.
    Skips if the title is already present in Notes.
    """
    if not NOTION_KEY:
        print("ERROR: NOTION_API_KEY not set")
        return False

    current_notes = _get_notes(project_id)

    # Dedup: extract title from content_line (everything before " - " or " [")
    # and check if it already appears in current notes
    title_fragment = content_line.split(" - ")[0].lstrip("• ").strip()
    if title_fragment and title_fragment in current_notes:
        print(f"⏭️  Already linked (skipping): {title_fragment}")
        return True  # Not an error — just already done

    new_notes = current_notes
    if current_notes and not current_notes.endswith("\n"):
        new_notes += "\n"
    new_notes += content_line

    if _write_notes(project_id, new_notes):
        print(f"✅ Linked: {content_line}")
        return True
    return False


def link_substack_article(title: str, url: str, status: str = "Scheduled") -> bool:
    """Link a Substack article to the Substack project."""
    content_line = f"• {title} - {url} - [{status}]"
    return update_project_notes(SUBSTACK_PROJECT_ID, content_line)


def link_linkedin_post(title: str, status: str = "Scheduled") -> bool:
    """Link a LinkedIn post to the LinkedIn Sage Agent project."""
    content_line = f"• {title} - [{status}]"
    return update_project_notes(LINKEDIN_PROJECT_ID, content_line)


def sync_published(days: int = 7, dry_run: bool = False):
    """
    Auto-sync: find all Published content in tracker DBs not yet linked to project pages.
    Runs for both Substack and LinkedIn.
    """
    if not NOTION_KEY:
        print("ERROR: NOTION_API_KEY not set")
        return

    cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
    linked = 0
    skipped = 0

    # --- Substack ---
    print(f"\n=== Substack Tracker (last {days} days) ===")
    substack_notes = _get_notes(SUBSTACK_PROJECT_ID)
    resp = requests.post(
        f"https://api.notion.com/v1/databases/{SUBSTACK_TRACKER_DB}/query",
        headers=_headers(),
        json={
            "page_size": 50,
            "filter": {
                "and": [
                    {"property": "Live on Substack", "checkbox": {"equals": True}},
                    {"timestamp": "created_time", "created_time": {"after": cutoff}}
                ]
            },
            "sorts": [{"timestamp": "created_time", "direction": "descending"}]
        }
    )
    if resp.status_code == 200:
        for page in resp.json().get("results", []):
            props = page.get("properties", {})
            title = next((v["title"][0]["plain_text"] for k, v in props.items()
                          if v.get("type") == "title" and v.get("title")), None)
            url_prop = props.get("Substack URL", {})
            url = url_prop.get("url", "") if url_prop.get("type") == "url" else ""
            if not title:
                continue
            if title in substack_notes:
                print(f"  ⏭️  Already linked: {title[:60]}")
                skipped += 1
                continue
            content_line = f"• {title} - {url or '(no url)'} - [Published]"
            print(f"  {'[DRY RUN] Would link' if dry_run else '➕ Linking'}: {title[:60]}")
            if not dry_run:
                substack_notes += ("\n" if substack_notes and not substack_notes.endswith("\n") else "") + content_line
                linked += 1
        if not dry_run and linked:
            _write_notes(SUBSTACK_PROJECT_ID, substack_notes)
    else:
        print(f"  ERROR querying Substack tracker: {resp.text}")

    # --- LinkedIn ---
    print(f"\n=== LinkedIn Tracker (last {days} days) ===")
    linkedin_notes = _get_notes(LINKEDIN_PROJECT_ID)
    resp = requests.post(
        f"https://api.notion.com/v1/databases/{LINKEDIN_TRACKER_DB}/query",
        headers=_headers(),
        json={
            "page_size": 50,
            "filter": {
                "and": [
                    {"property": "Post workflow", "status": {"equals": "Published"}},
                    {"timestamp": "created_time", "created_time": {"after": cutoff}}
                ]
            },
            "sorts": [{"timestamp": "created_time", "direction": "descending"}]
        }
    )
    if resp.status_code == 200:
        li_linked = 0
        for page in resp.json().get("results", []):
            props = page.get("properties", {})
            title = next((v["title"][0]["plain_text"] for k, v in props.items()
                          if v.get("type") == "title" and v.get("title")), None)
            if not title:
                continue
            if title in linkedin_notes:
                print(f"  ⏭️  Already linked: {title[:60]}")
                skipped += 1
                continue
            content_line = f"• {title} - [Published]"
            print(f"  {'[DRY RUN] Would link' if dry_run else '➕ Linking'}: {title[:60]}")
            if not dry_run:
                linkedin_notes += ("\n" if linkedin_notes and not linkedin_notes.endswith("\n") else "") + content_line
                li_linked += 1
                linked += 1
        if not dry_run and li_linked:
            _write_notes(LINKEDIN_PROJECT_ID, linkedin_notes)
    else:
        print(f"  ERROR querying LinkedIn tracker: {resp.text}")

    print(f"\n✅ Done — {linked} linked, {skipped} already present")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Link content to Notion projects")
    parser.add_argument("--type", choices=["substack", "linkedin", "sync"],
                        help="Content type or 'sync' to auto-sync all published")
    parser.add_argument("--title", help="Content title")
    parser.add_argument("--url", help="Content URL (for Substack)")
    parser.add_argument("--status", default="Published",
                        choices=["Draft", "Scheduled", "Published"],
                        help="Publication status")
    parser.add_argument("--days", type=int, default=7,
                        help="Lookback window in days for sync (default: 7)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Show what would be linked without writing")

    args = parser.parse_args()

    if args.type == "sync" or args.type is None:
        sync_published(days=args.days, dry_run=args.dry_run)
    elif args.type == "substack":
        if not args.title:
            print("ERROR: --title required")
            sys.exit(1)
        if not args.url:
            print("ERROR: --url required for Substack articles")
            sys.exit(1)
        success = link_substack_article(args.title, args.url, args.status)
        sys.exit(0 if success else 1)
    elif args.type == "linkedin":
        if not args.title:
            print("ERROR: --title required")
            sys.exit(1)
        success = link_linkedin_post(args.title, args.status)
        sys.exit(0 if success else 1)
