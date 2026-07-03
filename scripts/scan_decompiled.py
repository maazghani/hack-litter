#!/usr/bin/env python3
"""Scan decompiled Android sources/resources for smart-device integration clues."""
from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import Iterable

PATTERNS: dict[str, re.Pattern[str]] = {
    "urls": re.compile(r"https?://[^\s\"'<>\\)]+", re.I),
    "mqtt": re.compile(r"\b(mqtt|Mqtt|MQTT|tcp://|ssl://|1883|8883|broker|topic)\b"),
    "websocket": re.compile(r"\b(wss?://|WebSocket|OkHttpClient\.newWebSocket)\b", re.I),
    "ble_uuid": re.compile(r"\b[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}\b"),
    "tuya": re.compile(r"\b(tuya|smartlife|ThingSmart|TuyaSmart|IThing|com\.thingclips|com\.tuya)\b", re.I),
    "keys_ids": re.compile(r"\b(app[_-]?key|app[_-]?secret|product[_-]?id|pid|device[_-]?id|devId|client[_-]?id|region|env)\b", re.I),
    "pinning": re.compile(r"\b(CertificatePinner|TrustManager|HostnameVerifier|pinning|sha256/|network_security_config)\b", re.I),
    "auth": re.compile(r"\b(login|logout|token|refreshToken|accessToken|session|Authorization|Bearer|password|captcha)\b", re.I),
    "commands": re.compile(r"\b(clean|cleaning|stop|pause|reset|deodor|schedule|timer|record|alert|warning|fault|weight|toilet|litter|cat)\b", re.I),
}

SKIP_SUFFIXES = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".so", ".dex", ".arsc", ".mp3", ".ttf", ".otf", ".pyc"}
SKIP_DIRS = {".git", "__pycache__", ".gradle", "build"}


def iter_files(root: Path) -> Iterable[Path]:
    for path in root.rglob("*"):
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        if path.is_file() and path.suffix.lower() not in SKIP_SUFFIXES:
            yield path


def snippet(line: str, width: int = 220) -> str:
    clean = " ".join(line.strip().split())
    return clean[: width - 1] + "…" if len(clean) > width else clean


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path, help="Decompiled APK directory")
    parser.add_argument("--output", type=Path, help="Markdown report path")
    parser.add_argument("--max-per-category", type=int, default=80)
    args = parser.parse_args()

    if not args.root.is_dir():
        parser.error(f"not a directory: {args.root}")

    findings: dict[str, list[tuple[str, int, str]]] = {name: [] for name in PATTERNS}
    for path in iter_files(args.root):
        try:
            text = path.read_text(errors="ignore")
        except OSError:
            continue
        rel = path.relative_to(args.root)
        for lineno, line in enumerate(text.splitlines(), 1):
            for name, pattern in PATTERNS.items():
                if len(findings[name]) >= args.max_per_category:
                    continue
                if pattern.search(line):
                    findings[name].append((str(rel), lineno, snippet(line)))

    lines = ["# Kitten Mew decompiled scan", ""]
    for name, rows in findings.items():
        lines.append(f"## {name}")
        lines.append("")
        if not rows:
            lines.append("No matches found.")
        else:
            for file, lineno, text in rows:
                lines.append(f"- `{file}:{lineno}` — `{text}`")
        lines.append("")

    report = "\n".join(lines)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(report)
        print(f"Wrote {args.output}")
    else:
        print(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
