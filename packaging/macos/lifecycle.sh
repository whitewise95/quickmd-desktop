#!/bin/bash
# Shared installer operations. Explicit paths make the lifecycle independently testable.
quickmd_snapshot_file() {
    local source="$1" backup="$2"
    if [[ -e "$source" ]]; then
        cp -pL "$source" "$backup"
        : > "$backup.exists"
    fi
}

quickmd_restore_file() {
    local destination="$1" backup="$2"
    if [[ -f "$backup.exists" ]]; then
        if cmp -s "$backup" "$destination"; then return 0; fi
        cat "$backup" > "$destination"
    else
        rm -f "$destination"
    fi
}

quickmd_remove_path_block() {
    local profile="$1" temporary
    [[ -f "$profile" ]] || return 0
    temporary="$(mktemp "${profile}.quickmd.XXXXXX")" || return 1
    # Delete only the exact block we wrote. Incomplete or edited blocks survive intact.
    awk '
      BEGIN { start="# >>> QuickMD PATH >>>"; end="# <<< QuickMD PATH <<<";
              path="export PATH=\"$HOME/.local/bin:$PATH\"" }
      state == 0 && $0 == start { buffered=$0 ORS; state=1; next }
      state == 1 && $0 == path { buffered=buffered $0 ORS; state=2; next }
      state == 2 && $0 == end { buffered=""; state=0; next }
      state != 0 { printf "%s", buffered; buffered=""; state=0 }
      { print }
      END { printf "%s", buffered }
    ' "$profile" > "$temporary"
    cat "$temporary" > "$profile"
    rm -f "$temporary"
}

quickmd_remove_installation() {
    local user_home="$1" purge="$2"
    local root="$user_home/Library/Application Support/QuickMD"
    local workflow="$user_home/Library/Services/QuickMD — Markdown으로 변환.workflow"
    local target="$root/QuickMD.app/Contents/MacOS/quickmd"
    [[ -f "$root/.quickmd-install" ]] || { echo 'No official QuickMD installation found.' >&2; return 1; }
    if [[ -e "$workflow" || -L "$workflow" ]]; then
        [[ ! -L "$workflow" && ! -L "$workflow/Contents" ]] || return 1
        local owner
        owner="$(/usr/libexec/PlistBuddy -c 'Print :CFBundleIdentifier' "$workflow/Contents/Info.plist")"
        [[ "$owner" == org.quickmd.convert ]] || { echo 'Workflow ownership mismatch.' >&2; return 1; }
        rm -rf "$workflow"
    fi
    if [[ -L "$user_home/.local/bin/quickmd" && "$(readlink "$user_home/.local/bin/quickmd")" == "$target" ]]; then
        rm "$user_home/.local/bin/quickmd"
    fi
    quickmd_remove_path_block "$user_home/.zprofile"
    quickmd_remove_path_block "$user_home/.bash_profile"
    rm -rf "$root/QuickMD.app" "$root/queue"
    rm -f "$root/.quickmd-install"
    if [[ "$purge" == true ]]; then rm -rf "$root/logs"; fi
}
