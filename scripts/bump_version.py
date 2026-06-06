# -*- coding: utf-8 -*-
"""
Script tang version - Chay thu cong hoac tu dong qua pre-commit hook.

Usage:
    python scripts/bump_version.py patch   # 1.2.3 -> 1.2.4
    python scripts/bump_version.py minor   # 1.2.3 -> 1.3.0
    python scripts/bump_version.py major   # 1.2.3 -> 2.0.0
    python scripts/bump_version.py set 1.2.3   # Dat version cu the

Ghi chu:
    - Cap nhat src/config/app_config.py (VERSION, VERSION_MAJOR, VERSION_MINOR, VERSION_PATCH)
    - Cap nhat update.json (latest_version)
    - Ghi vao CHANGELOG.md
"""

import os
import re
import sys
import json
from datetime import date


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APP_CONFIG = os.path.join(ROOT, "src", "config", "app_config.py")
UPDATE_JSON = os.path.join(ROOT, "update.json")
CHANGELOG = os.path.join(ROOT, "CHANGELOG.md")


def get_current_version() -> tuple:
    with open(APP_CONFIG, "r", encoding="utf-8") as f:
        content = f.read()
    match = re.search(r'VERSION\s*=\s*["\']([\d.]+)["\']', content)
    if not match:
        raise ValueError("Khong tim thay VERSION trong app_config.py")
    return tuple(int(x) for x in match.group(1).split("."))


def bump_version(level: str, new_version: str = None) -> tuple:
    """Tang version va tra ve tuple (major, minor, patch)."""
    major, minor, patch = get_current_version()

    if new_version:
        parts = new_version.split(".")
        if len(parts) != 3:
            raise ValueError("Version phai co dinh dang x.y.z")
        return tuple(int(x) for x in parts)

    if level == "major":
        major += 1
        minor = 0
        patch = 0
    elif level == "minor":
        minor += 1
        patch = 0
    elif level == "patch":
        patch += 1
    else:
        raise ValueError(f"Unknown level: {level}")

    return major, minor, patch


def update_app_config(major: int, minor: int, patch: int):
    version_str = f"{major}.{minor}.{patch}"
    with open(APP_CONFIG, "r", encoding="utf-8") as f:
        content = f.read()

    content = re.sub(
        r'(VERSION\s*=\s*)["\'][^"\']+["\']',
        rf'\g<1>"{version_str}"',
        content
    )
    content = re.sub(
        r'(VERSION_MAJOR\s*=\s*)\d+',
        rf'\g<1>{major}',
        content
    )
    content = re.sub(
        r'(VERSION_MINOR\s*=\s*)\d+',
        rf'\g<1>{minor}',
        content
    )
    content = re.sub(
        r'(VERSION_PATCH\s*=\s*)\d+',
        rf'\g<1>{patch}',
        content
    )

    with open(APP_CONFIG, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"  [OK] app_config.py: VERSION = {version_str}")


def update_update_json(major: int, minor: int, patch: int, changelog_msg: str = ""):
    version_str = f"{major}.{minor}.{patch}"
    with open(UPDATE_JSON, "r", encoding="utf-8") as f:
        data = json.load(f)

    data["latest_version"] = version_str

    # Luon giu lai truong sha256 neu co
    if "sha256" not in data:
        data["sha256"] = ""

    # Cap nhat changelog neu co message
    if changelog_msg:
        data["changelog"] = changelog_msg
    elif os.path.exists(CHANGELOG):
        # Doc tu CHANGELOG.md entry dau tien
        try:
            with open(CHANGELOG, "r", encoding="utf-8") as f:
                content = f.read()
            # Tim entry dau tien
            match = re.search(r'## \[[\d.]+\].*?\n(.*?)(?=\n---\n|\n## \[)', content, re.DOTALL)
            if match:
                lines = match.group(1).strip().split("\n")
                summary = []
                for line in lines:
                    line = re.sub(r'^### \w+\s*', '', line)
                    line = re.sub(r'^\s*[-*]\s*', '', line)
                    line = line.strip()
                    if line:
                        summary.append(line)
                if summary:
                    data["changelog"] = "; ".join(summary[:3])
        except Exception:
            pass

    with open(UPDATE_JSON, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"  [OK] update.json: latest_version = {version_str}")


def update_changelog(major: int, minor: int, patch: int, level: str, files: list = None):
    version_str = f"{major}.{minor}.{patch}"
    today = date.today().strftime("%Y-%m-%d")

    # Xac dinh loai thay doi
    level_map = {"major": "MAJOR", "minor": "ADD", "patch": "FIX", "set": "SET"}
    change_type = level_map.get(level, "FIX")

    # Lay message tu commit hien tai (neu co)
    commit_msg = ""
    try:
        result = os.popen("git log -1 --pretty=%B 2>nul").read().strip()
        if result and not result.startswith("chore: tang cuong"):
            commit_msg = result
    except Exception:
        pass

    new_entry = f"## [{version_str}] - {today}\n\n### {change_type}\n"
    if commit_msg:
        new_entry += f"- {commit_msg}\n"
    elif files:
        new_entry += f"- Cap nhat: {', '.join(files[:5])}"
        if len(files) > 5:
            new_entry += f" va {len(files) - 5} file khac"
        new_entry += "\n"
    else:
        new_entry += "- Cap nhat code\n"

    new_entry += "\n---\n\n"

    with open(CHANGELOG, "r", encoding="utf-8") as f:
        content = f.read()

    # Chen sau header changelog
    header_end = content.find("## [")
    if header_end == -1:
        content = new_entry + content
    else:
        content = content[:header_end] + new_entry + content[header_end:]

    with open(CHANGELOG, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"  [OK] CHANGELOG.md: Da ghi entry {version_str}")


def main():
    if len(sys.argv) < 2:
        print("Usage: python bump_version.py [patch|minor|major|set X.Y.Z]")
        sys.exit(1)

    level = sys.argv[1]
    new_version = None

    if level == "set" and len(sys.argv) >= 3:
        new_version = sys.argv[2]
        level = "set"

    try:
        if new_version:
            major, minor, patch = bump_version("set", new_version)
        else:
            major, minor, patch = bump_version(level)

        old_major, old_minor, old_patch = get_current_version()
        old_str = f"{old_major}.{old_minor}.{old_patch}"
        new_str = f"{major}.{minor}.{patch}"

        print(f"\nTang version: {old_str} -> {new_str}")
        print("")

        update_app_config(major, minor, patch)
        update_update_json(major, minor, patch, level)
        update_changelog(major, minor, patch, level)

        print("")
        print(f"[VERSION CHECK]")
        print(f"  - src/config/app_config.py: VERSION = \"{new_str}\"  [OK]")
        print(f"  - update.json: latest_version = \"{new_str}\"         [OK]")
        print(f"  - CHANGELOG.md: Da ghi entry moi                    [OK]")
        print("")

        # Git add cac file da thay doi
        try:
            os.system('git add src/config/app_config.py update.json CHANGELOG.md')
            print("  [OK] Da git add cac file version")
        except Exception:
            pass

    except Exception as e:
        print(f"[ERROR] {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
