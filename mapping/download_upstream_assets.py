#!/usr/bin/env python3
"""Download optional upstream assets listed in UPSTREAM_ASSETS.json."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import urllib.request

def git_sha(data):
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--group", choices=["weights", "dataset", "assets", "all"], default="weights")
    parser.add_argument("--list", action="store_true", help="Only list matching files")
    args = parser.parse_args()
    root = Path(__file__).resolve().parent
    records = json.loads((root / "UPSTREAM_ASSETS.json").read_text())["files"]
    for item in records:
        if args.group != "all" and item["group"] != args.group:
            continue
        target = (root / item["path"]).resolve()
        if not target.is_relative_to(root):
            raise ValueError("Asset path escapes workspace")
        if args.list:
            print(item["path"], item["size"], item["url"])
            continue
        if target.exists():
            if git_sha(target.read_bytes()) != item["sha"]:
                raise FileExistsError(f"Different local file: {target}; move it before downloading")
            print("verified", item["path"])
            continue
        print("downloading", item["path"], flush=True)
        with urllib.request.urlopen(item["url"], timeout=180) as response:
            data = response.read()
        if len(data) != item["size"] or git_sha(data) != item["sha"]:
            raise ValueError(f"Upstream integrity check failed: {item['path']}")
        target.parent.mkdir(parents=True, exist_ok=True)
        temporary = target.with_name(target.name + ".download")
        temporary.write_bytes(data)
        os.replace(temporary, target)
if __name__ == "__main__":
    main()
