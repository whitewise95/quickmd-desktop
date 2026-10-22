#!/bin/bash
# Download only from an explicitly selected repository and tag; require a trusted hash.
set -euo pipefail
if [[ $# != 3 ]]; then
    echo 'Usage: bash install-macos.sh OWNER/REPO vVERSION TRUSTED_SHA256' >&2; exit 2
fi
repository="$1"; version="$2"; expected="$3"
[[ "$repository" =~ ^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$ ]] || exit 2
[[ "$version" =~ ^v[0-9]+\.[0-9]+\.[0-9]+$ ]] || exit 2
[[ "$expected" =~ ^[a-fA-F0-9]{64}$ ]] || exit 2
[[ "$(uname -s)" == Darwin ]] || exit 1
case "$(uname -m)" in arm64) arch=arm64 ;; x86_64) arch=x64 ;; *) exit 1 ;; esac
work="$(mktemp -d)"
mounted=false
cleanup() {
    if [[ "$mounted" == true ]]; then hdiutil detach "$work/mount" >/dev/null || true; fi
    rm -rf "$work"
}
trap cleanup EXIT
artifact="QuickMD-macOS-$arch.dmg"
curl --fail --location --proto '=https' --proto-redir '=https' --tlsv1.2 \
    "https://github.com/$repository/releases/download/$version/$artifact" -o "$work/$artifact"
actual="$(shasum -a 256 "$work/$artifact" | cut -d' ' -f1)"
[[ "$(printf '%s' "$expected" | tr '[:upper:]' '[:lower:]')" == "$actual" ]] || {
    echo 'SHA-256 mismatch; nothing installed.' >&2; exit 1;
}
spctl --assess --type open --context context:primary-signature "$work/$artifact"
mkdir "$work/mount"
hdiutil attach "$work/$artifact" -readonly -nobrowse -mountpoint "$work/mount" >/dev/null
mounted=true
bash "$work/mount/install.sh"
