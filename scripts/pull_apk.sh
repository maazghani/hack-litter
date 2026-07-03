#!/usr/bin/env bash
set -euo pipefail

PACKAGE="${1:-com.smart.trydow}"
OUT="${2:-./kitten-mew.apk}"

if ! command -v adb >/dev/null 2>&1; then
  echo "adb is not installed or not on PATH" >&2
  exit 127
fi

APK_PATH="$(adb shell pm path "$PACKAGE" | tr -d '\r' | sed -n 's/^package://p' | head -n 1)"
if [[ -z "$APK_PATH" ]]; then
  echo "Package not found on attached device/emulator: $PACKAGE" >&2
  exit 1
fi

adb pull "$APK_PATH" "$OUT"
echo "Pulled $PACKAGE from $APK_PATH to $OUT"
