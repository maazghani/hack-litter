# Kitten Mew smart litter box investigation

This repository contains the current investigation notes and repeatable tooling for the Android app **Kitten Mew** (`com.smart.trydow`), used with Mintakawa/LB500C-style smart litter boxes.

## Current status

No APK was present in this workspace, and no Android device/emulator with `com.smart.trydow` was available during this run. Because of that, no private endpoints, MQTT topics, BLE UUIDs, SDK keys, or command payloads have been extracted yet.

Known public identity from app store metadata:

- App name: Kitten mew
- Android package: `com.smart.trydow`
- iOS App Store ID: `6593670479`
- Stated functions: remote cleaning, timed cleaning, toilet records, and abnormal notifications

## Repository contents

- `scripts/pull_apk.sh` — pulls the APK from an attached Android device if the package is installed.
- `scripts/decompile_apk.sh` — decompiles an APK using `jadx`/`jadx-cli`.
- `scripts/scan_decompiled.py` — scans decompiled output for endpoints, SDK usage, BLE UUIDs, MQTT/WebSocket indicators, certificate pinning, auth/token terms, and likely litter-box commands.
- `docs/kitten-mew-report.md` — concise current report and practical next steps.
- `poc/.env.example` — placeholder configuration for future read-only proof-of-concept work.
- `poc/README.md` — safe PoC policy and workflow notes.

## Quick start

```bash
# 1. If the app is installed on an attached Android device/emulator
./scripts/pull_apk.sh

# 2. Or provide an APK manually, without committing it
cp /path/to/kitten-mew.apk ./kitten-mew.apk

# 3. Decompile
./scripts/decompile_apk.sh ./kitten-mew.apk ./decompiled/kitten-mew

# 4. Scan
python3 scripts/scan_decompiled.py ./decompiled/kitten-mew --output findings/kitten-mew-scan.md
```

## Safety

Do not commit APKs, credentials, tokens, private certificates, or device identifiers. The `.gitignore` is configured to exclude common reverse-engineering outputs and secret-bearing files.
