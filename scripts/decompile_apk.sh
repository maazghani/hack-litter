#!/usr/bin/env bash
set -euo pipefail

APK="${1:-./kitten-mew.apk}"
OUT_DIR="${2:-./decompiled/kitten-mew}"

if [[ ! -f "$APK" ]]; then
  echo "APK not found: $APK" >&2
  exit 1
fi

JADX_BIN=""
if command -v jadx >/dev/null 2>&1; then
  JADX_BIN="jadx"
elif command -v jadx-cli >/dev/null 2>&1; then
  JADX_BIN="jadx-cli"
else
  echo "jadx or jadx-cli is required" >&2
  exit 127
fi

mkdir -p "$OUT_DIR"
"$JADX_BIN" --deobf --show-bad-code --output-dir "$OUT_DIR" "$APK"
echo "Decompiled $APK to $OUT_DIR"
