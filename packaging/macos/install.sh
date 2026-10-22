#!/bin/bash
set -euo pipefail
umask 077

[[ "$(uname -s)" == Darwin ]] || { echo 'macOS is required.' >&2; exit 1; }
major="$(sw_vers -productVersion | cut -d. -f1)"
(( major >= 13 )) || { echo 'macOS 13 or later is required.' >&2; exit 1; }
source_dir="$(cd "$(dirname "$0")" && pwd)"
source "$source_dir/lifecycle.sh"
app_source="$source_dir/QuickMD.app"
[[ -x "$app_source/Contents/MacOS/quickmd" ]] || { echo 'App bundle is missing.' >&2; exit 1; }
architecture="$(uname -m)"
file "$app_source/Contents/MacOS/quickmd" | grep -q "$architecture" || {
    echo "Wrong CPU architecture: expected $architecture" >&2; exit 1;
}
# Developer builds can be tested locally. Downloaded builds remain subject to Gatekeeper.
codesign --verify --deep --strict "$app_source"
if xattr -p com.apple.quarantine "$app_source" >/dev/null 2>&1; then
    spctl --assess --type execute "$app_source"
fi
root="$HOME/Library/Application Support/QuickMD"
cli_dir="$HOME/.local/bin"
mkdir -p "$root" "$cli_dir"
mkdir "$root/install.lock" 2>/dev/null || { echo 'Another install is running.' >&2; exit 1; }
staging="$(mktemp -d "$root/.install.XXXXXX")"
snapshot_ready=false
installed=false
committed=false
rollback() {
    if [[ "$installed" == true && "$committed" == false ]]; then
        if [[ ! -d "$staging/previous.app" && -x "$target" ]]; then
            "$target" unintegrate >/dev/null 2>&1 || true
        fi
        rm -rf "$root/QuickMD.app"
        if [[ -d "$staging/previous.app" ]]; then
            mv "$staging/previous.app" "$root/QuickMD.app"
            "$root/QuickMD.app/Contents/MacOS/quickmd" integrate >/dev/null 2>&1 || true
        fi
        if [[ ! -d "$root/QuickMD.app" && -L "$cli_dir/quickmd" && "$(readlink "$cli_dir/quickmd")" == "$target" ]]; then
            rm "$cli_dir/quickmd"
        fi
        if [[ "$snapshot_ready" == true ]]; then
            quickmd_restore_file "$HOME/.zprofile" "$staging/zprofile"
            quickmd_restore_file "$HOME/.bash_profile" "$staging/bash_profile"
            quickmd_restore_file "$root/uninstall.sh" "$staging/uninstall"
            quickmd_restore_file "$root/lifecycle.sh" "$staging/lifecycle"
            quickmd_restore_file "$root/.quickmd-install" "$staging/marker"
        fi
    fi
    rm -rf "$staging"
    rmdir "$root/install.lock" 2>/dev/null || true
}
trap rollback EXIT
target="$root/QuickMD.app/Contents/MacOS/quickmd"
quickmd_snapshot_file "$HOME/.zprofile" "$staging/zprofile"
quickmd_snapshot_file "$HOME/.bash_profile" "$staging/bash_profile"
quickmd_snapshot_file "$root/uninstall.sh" "$staging/uninstall"
quickmd_snapshot_file "$root/lifecycle.sh" "$staging/lifecycle"
quickmd_snapshot_file "$root/.quickmd-install" "$staging/marker"
snapshot_ready=true
if [[ -e "$cli_dir/quickmd" || -L "$cli_dir/quickmd" ]]; then
    [[ -L "$cli_dir/quickmd" && "$(readlink "$cli_dir/quickmd")" == "$target" ]] || {
        echo 'Existing ~/.local/bin/quickmd belongs to another installation.' >&2; exit 1;
    }
fi
if [[ -e "$root/QuickMD.app" ]]; then
    [[ -f "$root/.quickmd-install" && ! -L "$root/QuickMD.app" ]] || {
        echo 'Unrecognized existing application; refusing to replace it.' >&2; exit 1;
    }
fi
ditto "$app_source" "$staging/QuickMD.app"
"$staging/QuickMD.app/Contents/MacOS/quickmd" doctor --no-integration
if [[ -d "$root/QuickMD.app" ]]; then mv "$root/QuickMD.app" "$staging/previous.app"; fi
installed=true
mv "$staging/QuickMD.app" "$root/QuickMD.app"
"$target" integrate
"$target" doctor
cp "$source_dir/uninstall.sh" "$root/uninstall.sh"
cp "$source_dir/lifecycle.sh" "$root/lifecycle.sh"
chmod 700 "$root/uninstall.sh"
ln -sfn "$target" "$cli_dir/quickmd"
# A dedicated marker block is removed by the uninstaller. Other PATH entries are untouched.
for profile in "$HOME/.zprofile" "$HOME/.bash_profile"; do
    if ! grep -q '^# >>> QuickMD PATH >>>$' "$profile" 2>/dev/null; then
        printf '\n# >>> QuickMD PATH >>>\nexport PATH="$HOME/.local/bin:$PATH"\n# <<< QuickMD PATH <<<\n' >> "$profile"
    fi
done
printf 'QuickMD user installation\n' > "$root/.quickmd-install"
committed=true
echo 'QuickMD installed. Open a new terminal for PATH changes.'
echo 'Finder: select a supported file > Quick Actions > Markdown으로 변환.'
echo 'If hidden, enable the service in System Settings. Finder visibility needs a manual check.'
