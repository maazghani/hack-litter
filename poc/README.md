# Kitten Mew read-only PoC

This directory contains a guarded, read-only Tuya/Thing OpenAPI discovery helper for the Kitten Mew smart litter box investigation.

## Files

- `.env.example` — copy to `poc/.env` and fill with Tuya IoT Cloud credentials and a device ID you own.
- `tuya_readonly.py` — signs Tuya OpenAPI requests and performs only read-only token, device details, status, functions, and specification calls.

## Usage

```bash
cp poc/.env.example poc/.env
# edit poc/.env with your own Tuya Cloud project credentials and owned device ID
python3 poc/tuya_readonly.py
```

## Safety rules

1. Load credentials and tokens from `poc/.env` only.
2. Start with authentication and read-only device/status/functions/specification calls.
3. Keep `DRY_RUN=true` by default.
4. Do not add command/control calls until DP IDs, enum values, and physical behavior are confirmed.
5. Require explicit `DRY_RUN=false` before any future command that may move hardware, clean, reset, deodorize, or change schedules.
6. Never commit credentials, tokens, APKs, private certificates, real device identifiers, or scan outputs containing user/device data.
