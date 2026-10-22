#!/bin/bash
set -euo pipefail
root="$HOME/Library/Application Support/QuickMD"
source "$(cd "$(dirname "$0")" && pwd)/lifecycle.sh"
purge=false
wait_pid=''
while (( $# )); do
    case "$1" in
        --purge-logs) purge=true; shift ;;
        --wait-pid) wait_pid="$2"; shift 2 ;;
        *) echo "Unknown option" >&2; exit 2 ;;
    esac
done
if [[ -n "$wait_pid" ]]; then
    [[ "$wait_pid" =~ ^[0-9]+$ ]] || exit 2
    while kill -0 "$wait_pid" 2>/dev/null; do sleep 0.2; done
fi
[[ -f "$root/.quickmd-install" ]] || { echo 'No official QuickMD installation found.'; exit 1; }
mkdir "$root/install.lock" 2>/dev/null || { echo 'Another installer is running.' >&2; exit 1; }
trap 'rmdir "$root/install.lock" 2>/dev/null || true' EXIT
quickmd_remove_installation "$HOME" "$purge"
/System/Library/CoreServices/pbs -update >/dev/null 2>&1 || true
# The shell has parsed this final command before its own script is removed.
rm -f "$root/uninstall.sh" "$root/lifecycle.sh"
echo 'QuickMD removed. Converted Markdown files and (by default) logs are preserved.'
