#!/usr/bin/env python3
"""Rewrite only AI co-author trailers, preserving commit trees and identities."""
from __future__ import annotations

import json
import os
from pathlib import Path
import re
import subprocess


AI_TRAILER = re.compile(rb"^Co-authored-by:.*(?:\bClaude\b|@anthropic\.com)", re.I)


def git(*args: str, data: bytes | None = None) -> bytes:
    return subprocess.check_output(["git", *args], input=data)


def split_commit(raw: bytes) -> tuple[list[bytes], bytes]:
    header, message = raw.split(b"\n\n", 1)
    blocks: list[bytes] = []
    for line in header.split(b"\n"):
        if line.startswith(b" "):
            if not blocks:
                raise ValueError("Invalid continuation header")
            blocks[-1] += b"\n" + line
        else:
            blocks.append(line)
    return blocks, message


def values(headers: list[bytes], key: bytes) -> list[bytes]:
    return [line[len(key) + 1:] for line in headers if line.startswith(key + b" ")]


def clean_message(message: bytes) -> bytes:
    return b"".join(line for line in message.splitlines(keepends=True) if not AI_TRAILER.match(line))


def rewrite(head: str) -> dict:
    commits = git("rev-list", "--topo-order", "--reverse", head).decode().splitlines()
    mapping: dict[str, str] = {}
    edited = 0
    signatures_removed = 0
    for old in commits:
        raw = git("cat-file", "commit", old)
        headers, message = split_commit(raw)
        new_message = clean_message(message)
        new_headers: list[bytes] = []
        for block in headers:
            if block.startswith(b"parent "):
                parent = block[7:].decode("ascii")
                new_headers.append(b"parent " + mapping[parent].encode("ascii"))
            else:
                new_headers.append(block)
        if new_headers == headers and new_message == message:
            mapping[old] = old
            continue
        if new_message != message:
            edited += 1
        # A changed commit cannot retain the old commit/tag signature.
        signed = (b"gpgsig ", b"gpgsig-sha256 ", b"mergetag ")
        signatures_removed += sum(block.startswith(signed) for block in new_headers)
        new_headers = [block for block in new_headers if not block.startswith(signed)]
        replacement = b"\n".join(new_headers) + b"\n\n" + new_message
        new = git("hash-object", "-t", "commit", "-w", "--stdin", data=replacement).decode().strip()
        mapping[old] = new

    # Validate every commit, including merge topology and original timestamps.
    for old, new in mapping.items():
        oh, om = split_commit(git("cat-file", "commit", old))
        nh, nm = split_commit(git("cat-file", "commit", new))
        for field in (b"tree", b"author", b"committer", b"encoding"):
            if values(oh, field) != values(nh, field):
                raise AssertionError(f"Changed {field!r}: {old}")
        expected_parents = [mapping[parent.decode()].encode() for parent in values(oh, b"parent")]
        if values(nh, b"parent") != expected_parents:
            raise AssertionError(f"Changed topology: {old}")
        if nm != clean_message(om) or any(AI_TRAILER.match(line) for line in nm.splitlines()):
            raise AssertionError(f"Unexpected message: {old}")

    new_head = mapping[head]
    if len(git("rev-list", new_head).splitlines()) != len(commits):
        raise AssertionError("Commit count changed")
    if git("rev-parse", head + "^{tree}") != git("rev-parse", new_head + "^{tree}"):
        raise AssertionError("Current code changed")
    return {
        "old_head": head,
        "new_head": new_head,
        "tree": git("rev-parse", new_head + "^{tree}").decode().strip(),
        "commits": len(commits),
        "edited_messages": edited,
        "rebuilt_commits": sum(old != new for old, new in mapping.items()),
        "signatures_removed": signatures_removed,
    }


def remote_head(ref: str) -> str:
    rows = git("ls-remote", "origin", ref).decode().strip().splitlines()
    if len(rows) != 1:
        raise RuntimeError(f"Cannot resolve {ref}")
    return rows[0].split()[0]


def main():
    expected = os.environ["EXPECTED_MAIN"]
    expected_repo = os.environ["EXPECTED_REPOSITORY"]
    backup = os.environ["BACKUP_BRANCH"]
    if os.environ.get("GITHUB_REPOSITORY") != expected_repo:
        raise RuntimeError("Unexpected repository")
    if not re.fullmatch(r"[a-f0-9]{40}", expected):
        raise ValueError("Invalid expected head")
    if remote_head("refs/heads/main") != expected:
        raise RuntimeError("Main changed; refusing to overwrite")
    if remote_head("refs/heads/" + backup) != expected:
        raise RuntimeError("Verified backup missing")
    report = rewrite(expected)
    print(json.dumps(report, indent=2), flush=True)
    if report["edited_messages"] == 0:
        raise RuntimeError("No matching AI trailers; refusing unexpected rewrite")
    if remote_head("refs/heads/main") != expected:
        raise RuntimeError("Main changed during rewrite")
    git("push", "--force-with-lease=refs/heads/main:" + expected,
        "origin", report["new_head"] + ":refs/heads/main")
    if remote_head("refs/heads/main") != report["new_head"]:
        raise RuntimeError("Published head verification failed")
    if remote_head("refs/heads/" + backup) != expected:
        raise RuntimeError("Backup changed")
    report["published"] = True
    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary:
        Path(summary).write_text("# Co-author cleanup verified\n\n```json\n" +
                                 json.dumps(report, indent=2) + "\n```\n")
    print("VERIFIED_PUBLISHED " + json.dumps(report), flush=True)


if __name__ == "__main__":
    main()
