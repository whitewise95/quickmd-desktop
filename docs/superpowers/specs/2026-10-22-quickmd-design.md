# QuickMD implementation design

The supplied [requirements](../../requirements.ko.md) are the product brief and authorization to implement. This is a new architectural project. No GUI, daemon, API key, OCR or remote document processing.

Use Python 3.12 and MarkItDown 0.1.9 with only PDF/DOCX/PPTX/XLSX extras. Validate local regular files, snapshot them into a private temporary directory, check OOXML archive expansion, then run conversion in a subprocess with time and memory bounds. Disable plugins and network access in the conversion worker. Source and output are never passed through a shell command string.

Write UTF-8 to a private temporary file on the destination filesystem, fsync, then publish with an atomic hard link that fails if the destination exists. Retry numbered names. Fail safely on filesystems without hard links. No overwrite fallback.

CLI and OS handlers share batch conversion. A user-scoped advisory file lock serializes expensive conversions. Windows legacy Player verbs enqueue each invocation; a lock holder drains the queue and summarizes results. macOS Automator Run Shell Script passes all arguments with quoted "$@". Shell commands use the absolute installed launcher; source-mode launchers use an absolute interpreter and -m quickmd.

Windows per-user Inno installer owns binaries, PATH and Start Menu AUMID. Python owns supported-extension registry verbs. macOS installer owns a versioned user-directory application, symlink in ~/.local/bin, Quick Action and a native notification helper. Uninstall launches an external script/official uninstaller after the process exits.

Notifications are best effort: Windows ToastNotificationManager with an installed AUMID shortcut; macOS UserNotifications helper inside the app bundle. Doctor distinguishes unavailable, disabled, unconfirmed and functional states.

CI builds on each target OS/CPU. Releases are development previews; no security bypass. No invented repository URL, package ID or package-manager availability.

Verification: real four-format fixtures, encrypted/broken/empty PDFs, malformed inputs, parallel output publication, timeouts, duplicates, mixed failures, paths and generated integration payloads. Automator execution and native packaging on this host where permitted. Explorer, Finder visibility, notifications and Gatekeeper require a recorded manual matrix.
