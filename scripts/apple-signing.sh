#!/bin/bash
set -euo pipefail
if [[ -z "${APPLE_CERT_P12_BASE64:-}" ]]; then
    echo 'No signing secrets: building development artifacts.'
    exit 0
fi
: "${APPLE_CERT_PASSWORD:?Required with certificate}"
: "${APPLE_SIGN_IDENTITY:?Required with certificate}"
keychain="$RUNNER_TEMP/quickmd.keychain-db"
certificate="$RUNNER_TEMP/quickmd-sign.p12"
keychain_password="$(openssl rand -hex 32)"
trap 'rm -f "$certificate"' EXIT
printf '%s' "$APPLE_CERT_P12_BASE64" | base64 --decode > "$certificate"
security create-keychain -p "$keychain_password" "$keychain"
security set-keychain-settings -lut 21600 "$keychain"
security unlock-keychain -p "$keychain_password" "$keychain"
security import "$certificate" -P "$APPLE_CERT_PASSWORD" -A -t cert -f pkcs12 -k "$keychain"
security set-key-partition-list -S apple-tool:,apple: -k "$keychain_password" "$keychain"
security list-keychains -d user -s "$keychain" login.keychain-db
printf 'APPLE_SIGN_IDENTITY=%s\n' "$APPLE_SIGN_IDENTITY" >> "$GITHUB_ENV"
if [[ -n "${APPLE_ID:-}" && -n "${APPLE_TEAM_ID:-}" && -n "${APPLE_APP_PASSWORD:-}" ]]; then
    xcrun notarytool store-credentials quickmd-notary --apple-id "$APPLE_ID" \
        --team-id "$APPLE_TEAM_ID" --password "$APPLE_APP_PASSWORD" --keychain "$keychain"
    printf 'APPLE_NOTARY_PROFILE=quickmd-notary\n' >> "$GITHUB_ENV"
fi
