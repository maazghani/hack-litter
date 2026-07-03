# Kitten Mew / Mintakawa LB500C integration report

## Investigation inputs

- APK source inspected: APKPure XAPK for `com.smart.trydow`, version `1.0.8`, downloaded outside the repository to `/tmp/kitten-mew/kitten-mew.xapk`.
- APKPure metadata advertised XAPK format, `arm64-v8a`, Android 6.0+, package `com.smart.trydow`, signature `8d37e90840dc071aad8ae30884e3121654feeb21`, and SHA-256 `e94690e4b9734669fa53f54f1b9440053c44afd66374da40dbe6f4c666be4eb4`.
- The downloaded XAPK hash matched APKPure's published SHA-256.
- The XAPK contained a base APK (`com.smart.trydow.apk`) and an `arm64-v8a` split APK.
- Decompiled output was kept in `/tmp/kitten-mew/decompiled` and was not committed.

## Package/app identity

- App name: Kitten mew / Kitten Mew.
- Android package: `com.smart.trydow`.
- Decompiled manifest version: `versionName="1.0.8"`, `versionCode="11"`.
- Decompiled application class: `com.smart.app.SmartApplication`.
- OEM alias/config package: `com.trydow.smart`.
- App scheme / TTID: `cactuscatmiaooo`.
- App ID in Thing/Thingclips config: `1656511147`.
- Cactus-branded records in config strongly suggest this is a Thingclips/Tuya OEM app package for Dongguan Cactus / Trydow-style devices rather than a fully custom standalone app.

## Communication model

**Primary model: Thingclips/Tuya OEM cloud + MQTT + dynamic device panels.**

Evidence:

- The app initializes `ThingSmartSdk`, `ThingSdk`, `ThingSmartNetWork`, and Thingclips `AppInitializer` from `SmartApplication`.
- The manifest includes `com.thingclips.smart.mqtt.MqttService`, `com.thingclips.sdk.blelib.BluetoothService`, Matter NSD discovery services, and many Thingclips activities/services.
- Open-source notices list `mqttv3`, `React-native`, `Matter`, `Android-BluetoothKit`, `Android-nRF-Mesh-Library`, `OkHttp`, and related SDK components.
- The app enables neutral Thing domains, encrypted/network security, HTTPS DNS configuration, device cache, and optional SSL pinning through Thingclips network configuration.
- Device control is exposed through Thingclips SDK abstractions such as `IThingDevice.publishDps(...)`, `IThingGateway.publishDpsByHttp(...)`, `IThingGateway.publishDpsByMqtt(...)`, timers, schemas, and device beans.

This means the litter box is very likely controlled as a Tuya/Thingclips data-point (DP) device. The app APK does **not** appear to contain a hardcoded litter-box-specific REST endpoint or command table; those are normally fetched from the Thing/Tuya cloud as product schema and/or dynamic mini-program/panel assets after login and device selection.

## Notable libraries/SDKs

- Thingclips/Tuya OEM SDK: `com.thingclips.*`, including base SDK, home, device, BLE, MQTT, Matter, miniapp/panel, and user/login modules.
- MQTT: Eclipse Paho `mqttv3` plus Thingclips MQTT service/classes.
- BLE: Thingclips BLE library, Android-BluetoothKit, nRF Mesh, Telink mesh UUIDs, Tuya BLE config UUIDs.
- Matter: CHIP/Matter discovery and Matter SDK components.
- React Native / miniapp panels: React Native and Thing miniapp/webview assets, suggesting device UI panels are dynamic and may be product-specific.
- OkHttp/Okio, RxJava, Fastjson/Gson, Firebase, Amazon login, LeakCanary/kshark, Tencent Mars/MMKV, BouncyCastle/OpenSSL/mbedtls/curl.

## Endpoints, brokers, and domains found

No litter-box-specific first-party REST API endpoint was found in the APK. The static endpoints/domains are generic SDK infrastructure, including:

- `thing.miniapp.com` and per-region miniapp webview hosts.
- Amazon login endpoints (`na.account.amazon.com`, `eu.account.amazon.com`, `apac.account.amazon.com`, `api.amazon.com`, etc.) from Amazon auth libraries.
- Firebase installation service endpoint.
- Encrypted Thing domain data under `resources/assets/thing_domains_v1/regions`.

The actual Thing/Tuya API hosts and MQTT brokers are probably selected at runtime by the Thingclips SDK from encrypted region/domain config and account region.

## BLE/Matter UUIDs found

The APK includes generic Thing/Tuya BLE, mesh, and Matter UUIDs, including:

- Matter/CHIP service UUIDs: `0000FFF6-0000-1000-8000-00805F9B34FB`, `0000FD50-0000-1000-8000-00805F9B34FB`.
- Thing BLE service/characteristics: `0000fd50-0000-1000-8000-00805f9b34fb`, `00000001-0000-1001-8001-00805F9B07D0`, `00000002-0000-1001-8001-00805F9B07D0`, `00000003-0000-1001-8001-00805F9B07D0`.
- Tuya BLE config UUIDs: `00001000-7475-7961-626c-636f6e666967`, `00001001-7475-7961-626c-636f6e666967`, `00001002-7475-7961-626c-636f6e666967`.
- Mesh/Telink-related UUIDs such as `00010203-0405-0607-0809-0a0b0c0d1910` / `1912` / `1914` and standard GATT/service UUIDs.

These prove BLE provisioning/local transport support in the SDK, but not that the litter box itself is BLE-controlled after provisioning.

## Keys, product IDs, and config

- Thing Smart app key and app secret are present in `com.thingclips.sample.BuildConfig`, but are intentionally **not reproduced here**. Treat them as vendor app credentials embedded in the public APK, not user secrets.
- Thing/NG config contains an app encrypt key/secret pair; also intentionally **not reproduced here**.
- Generic/product-adjacent IDs found include `hugolog_station_pids=b4f2rzqixqfnxsja`, `thing_subdevice_activator_pid=vtspamtituud0or2`, and `csa_vid=4701`. These are not confirmed as the LB500C litter-box product ID.
- The actual litter-box product ID and DP schema were not statically present in an obvious form. They should be retrieved from an account that owns the device via the Thing/Tuya cloud or by inspecting runtime panel/schema traffic.

## Certificate pinning / transport security

The app configures Thingclips networking with `supportSSLPinning(getResources().getBoolean(...))`. The referenced boolean resolves through generated resources and should be checked in runtime/resource tables, but the important point is that the SDK path supports SSL pinning. Do not bypass pinning or accounts. Prefer official Tuya/Thing OpenAPI or SDK-backed flows for integration.

## Command names / payload structures

No litter-box-specific command names such as clean/deodorize/reset were found as hardcoded app payloads. The relevant control API is Thing/Tuya DP publishing:

```java
IThingDevice.publishDps(String dpsJson, IResultCallback callback)
IThingDevice.publishDps(String dpsJson, ThingDevicePublishModeEnum mode, IResultCallback callback)
IThingGateway.publishDpsByHttp(String devId, String dpsJson, IResultCallback callback)
IThingGateway.publishDpsByMqtt(String devId, String dpsJson, IResultCallback callback)
```

A typical command payload in this ecosystem is a JSON object mapping DP IDs to values, for example `{"101": true}` or `{"1": "some_enum"}`. **The correct DP IDs and allowed values for cleaning, stop, deodorize, schedules, records, alerts, and weight must be discovered from the device's product schema before sending any write command.**

## Alexa/Home Assistant feasibility

Feasibility looks **good**, but the safest route is not reverse-engineering a custom REST API. This is a Thingclips/Tuya OEM app, so use one of these paths:

1. **Best first attempt: Tuya/Smart Life ecosystem linking.** Try adding the device to Tuya Smart or Smart Life using the same account/region or the OEM app's supported linking path. If the device appears, Home Assistant's Tuya integration and Alexa's Tuya/Smart Life skill may work with minimal custom code.
2. **If OEM-only account/device:** create a Tuya IoT Cloud project and attempt account/device linking for the same region. Query the device schema/status through official Tuya OpenAPI before any writes.
3. **If cloud APIs expose the device but standard HA entities are missing:** implement a Home Assistant custom integration that maps Tuya DP schema to litter-box entities (status sensors, last record sensors, alerts, and command buttons). Keep command buttons disabled/dry-run until DP values are confirmed.
4. **If only BLE provisioning/local control is available:** local Home Assistant integration may still be possible, but it would require BLE protocol work and is a second-choice path.

## Safest next step

Use a device-owning account to perform read-only schema/status discovery:

1. Pair the litter box normally in Kitten Mew.
2. In Tuya IoT Cloud, create a cloud project in the same region and link the app/account if possible.
3. Use official Tuya OpenAPI to list devices and query device status/functions/specifications.
4. Record DP IDs, names, types, ranges/enums, and read/write capability.
5. Only after read-only schema is documented, add a guarded PoC with `DRY_RUN=true` by default.

## Proof-of-concept status

A command-triggering PoC is still intentionally not included because the device-specific DP schema has not been obtained. The next PoC should be a read-only Tuya OpenAPI script that:

- Loads `TUYA_ACCESS_ID`, `TUYA_ACCESS_SECRET`, region endpoint, and target device ID from `.env`.
- Requests an access token.
- Calls read-only device status/specification endpoints.
- Writes output with device IDs redacted.
- Refuses all write/control calls unless `DRY_RUN=false` and a known-safe DP mapping is explicitly provided.
