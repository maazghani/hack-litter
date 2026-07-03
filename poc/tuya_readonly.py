#!/usr/bin/env python3
"""Read-only Tuya/Thing OpenAPI discovery helper for Kitten Mew devices.

This script intentionally performs only token, device status, functions, and
specification reads. It has no command/write path.
"""
from __future__ import annotations

import argparse
import hashlib
import hmac
import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any


DEFAULT_ENDPOINT = "https://openapi.tuyaus.com"
READ_ONLY_PATHS = (
    "/v1.0/devices/{device_id}",
    "/v1.0/devices/{device_id}/status",
    "/v1.0/devices/{device_id}/functions",
    "/v1.0/devices/{device_id}/specifications",
)


def load_env(path: Path) -> None:
    if not path.exists():
        return
    for raw in path.read_text().splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def body_hash(body: bytes = b"") -> str:
    return hashlib.sha256(body).hexdigest()


def sign(access_id: str, access_secret: str, method: str, path_with_query: str, timestamp: str, token: str = "", body: bytes = b"") -> str:
    string_to_sign = "\n".join([method.upper(), body_hash(body), "", path_with_query])
    payload = f"{access_id}{token}{timestamp}{string_to_sign}"
    return hmac.new(access_secret.encode(), payload.encode(), hashlib.sha256).hexdigest().upper()


def request_json(endpoint: str, access_id: str, access_secret: str, method: str, path: str, token: str = "") -> dict[str, Any]:
    endpoint = endpoint.rstrip("/")
    timestamp = str(int(time.time() * 1000))
    headers = {
        "client_id": access_id,
        "sign": sign(access_id, access_secret, method, path, timestamp, token),
        "t": timestamp,
        "sign_method": "HMAC-SHA256",
    }
    if token:
        headers["access_token"] = token
    req = urllib.request.Request(endpoint + path, method=method.upper(), headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", "replace")
        raise SystemExit(f"HTTP {exc.code} for {path}: {detail}") from exc


def redact_device_ids(data: Any, device_id: str) -> Any:
    if isinstance(data, dict):
        return {key: redact_device_ids(value, device_id) for key, value in data.items()}
    if isinstance(data, list):
        return [redact_device_ids(item, device_id) for item in data]
    if isinstance(data, str) and device_id and device_id in data:
        return data.replace(device_id, "<TUYA_DEVICE_ID>")
    return data


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--env-file", type=Path, default=Path(__file__).with_name(".env"))
    parser.add_argument("--endpoint", default=None, help="Tuya OpenAPI endpoint, e.g. https://openapi.tuyaus.com")
    parser.add_argument("--device-id", default=None)
    parser.add_argument("--no-redact", action="store_true", help="Print real device IDs in output")
    args = parser.parse_args()

    load_env(args.env_file)
    access_id = os.environ.get("TUYA_ACCESS_ID", "")
    access_secret = os.environ.get("TUYA_ACCESS_SECRET", "")
    endpoint = args.endpoint or os.environ.get("TUYA_REGION_ENDPOINT", DEFAULT_ENDPOINT)
    device_id = args.device_id or os.environ.get("TUYA_DEVICE_ID", "")

    missing = [name for name, value in {
        "TUYA_ACCESS_ID": access_id,
        "TUYA_ACCESS_SECRET": access_secret,
        "TUYA_DEVICE_ID": device_id,
    }.items() if not value]
    if missing:
        raise SystemExit(f"Missing required configuration: {', '.join(missing)}")

    token_response = request_json(endpoint, access_id, access_secret, "GET", "/v1.0/token?grant_type=1")
    if not token_response.get("success"):
        raise SystemExit(json.dumps(token_response, indent=2))
    token = token_response["result"]["access_token"]

    output: dict[str, Any] = {"endpoint": endpoint, "reads": {}}
    for template in READ_ONLY_PATHS:
        path = template.format(device_id=urllib.parse.quote(device_id, safe=""))
        output["reads"][path] = request_json(endpoint, access_id, access_secret, "GET", path, token)

    if not args.no_redact:
        output = redact_device_ids(output, device_id)
    print(json.dumps(output, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
