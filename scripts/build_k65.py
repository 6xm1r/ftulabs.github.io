#!/usr/bin/env python3
"""build_k65.py — Collect k65/members/<username>.json into k65/members.json.

Each K65 student adds only their own file, so pull requests never conflict.
Run with --check to validate without writing (used on pull requests).
"""

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MEMBERS = ROOT / "k65" / "members"
OUT = ROOT / "k65" / "members.json"
USERNAME = re.compile(r"^[A-Za-z0-9](?:[A-Za-z0-9-]{0,38})$")


def load(path):
    errors = []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        return None, [f"{path.name}: not valid JSON ({e})"]
    if not isinstance(data, dict):
        return None, [f"{path.name}: must be a JSON object"]

    name = str(data.get("name", "")).strip()
    github = str(data.get("github", "")).strip()
    if not name:
        errors.append(f'{path.name}: "name" is required')
    if github.lower() != path.stem.lower():
        errors.append(f'{path.name}: "github" must match the file name ({path.stem})')
    if not USERNAME.match(github):
        errors.append(f'{path.name}: "github" is not a valid GitHub username')
    links = data.get("links", {}) or {}
    if not isinstance(links, dict) or not all(
        isinstance(v, str) and v.startswith(("https://", "http://")) for v in links.values()
    ):
        errors.append(f'{path.name}: "links" must map labels to http(s) URLs')

    member = {
        "name": name[:80],
        "github": github,
        "role": str(data.get("role", "K65")).strip()[:60] or "K65",
        "bio": str(data.get("bio", "")).strip()[:280],
        "links": {str(k)[:24]: v for k, v in links.items()} if isinstance(links, dict) else {},
    }
    return member, errors


def main():
    check = "--check" in sys.argv
    members, errors = [], []
    for path in sorted(MEMBERS.glob("*.json")):
        if path.name.startswith("_"):
            continue
        member, errs = load(path)
        errors += errs
        if member and not errs:
            members.append(member)

    for e in errors:
        print(f"::error::{e}")
    if errors:
        sys.exit(1)

    members.sort(key=lambda m: m["name"].lower())
    text = json.dumps(members, ensure_ascii=False, indent=2) + "\n"
    if check:
        print(f"ok: {len(members)} member file(s) valid")
        return
    OUT.write_text(text, encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)} with {len(members)} member(s)")


if __name__ == "__main__":
    main()
