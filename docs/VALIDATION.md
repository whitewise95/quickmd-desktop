# Validation report — 2026-10-22 (Asia/Seoul)

This is a development implementation, not a verified public release.

## Environment and scope

- Host: macOS arm64. `sw_vers` reports 26.6.2; some Python runtime/diagnostic APIs report Darwin 25.6.0. Record the actual target's OS build again during acceptance testing.
- Python 3.12.10, MarkItDown 0.1.9, PyInstaller 6.22.3.
- Initially empty repository with no package-manager registration.
- Changes are local. No GitHub Actions run, public Release, package registration or live user-profile installation was performed.

## Observed checks

| Check | Result |
|---|---|
| `pytest -q` | **36 passed, 1 skipped**. Skipped test: native Windows registry lifecycle. |
| Actual PDF/DOCX/PPTX/XLSX | Source API tests and packaged app converted all four fixtures; expected text present; original SHA-256 unchanged in source test. |
| Errors and continuation | Corrupt/encrypted PDF, invalid input, empty result, input size and Office format mismatch, mixed-failure batches tested. |
| Resource bounds | Deliberately sleeping and memory-allocating child processes terminated; normal batch continues. |
| Output safety | 20 concurrent thread publications and 12 independent-process publications: unique complete files, existing contents preserved; existing output symlink not followed. |
| Batch/queue | 1/2/10/50-file batches; duplicate requests; independent concurrent shell-handler calls for all four formats; queue drained. |
| Paths/integration payload | Korean, spaces, apostrophe and shell metacharacters, leading-hyphen argv; real generated shell script forwards exact path array. Symlinked workflow Contents rejected by a failing-then-passing regression test. |
| Privacy | Logs contain conversion status, not fixture contents, full source paths or file names. |
| macOS lifecycle helpers | Complete block removal; malformed/edited PATH block preservation; removal with missing app executable; file snapshot/restore; unrelated Markdown/log preservation. |
| Generated Quick Action | Executed with native `automator` against a Korean/space-named PDF in the workspace. Markdown was created with expected text. No live Finder service registration used. |
| Notifications | Native Swift helper compiled; `--status` returned `not-determined`. Permission prompt/display delivery not tested. |
| Frozen app | Native arm64 PyInstaller app built. `doctor --no-integration` passed actual PDF conversion. All four formats converted using bundled executable, without source PYTHONPATH. |
| DMG | Development arm64 DMG generated with hdiutil. Integrity files in `dist/`. |
| Static checks | Ruff lint/format clean; strict mypy passes for host and `--platform win32`; Python compileall and Bash syntax checks pass. |
| Workflow | YAML parsed successfully. Current official Action releases checked; retiring macos-14 runner replaced with macos-15. Workflow execution remains unverified. |
| Dependencies | Universal uv lock includes conditional Windows dependencies. `pip install --require-hashes -r requirements-dev.lock --dry-run` resolved successfully on host. |
| Package registration preparation | Test-identity WinGet manifest generated and parsed; Homebrew cask passes Ruby syntax. No real registry submission/schema audit claimed. |

## Review and changes

An independent agent reviewed conversion, publication, argument forwarding and installer paths. Three macOS lifecycle findings were fixed:

1. Incomplete PATH marker blocks no longer truncate unrelated shell configuration.
2. Official removal can clean owned registration/links even when the app executable is missing.
3. Installation snapshots app/profile/uninstaller/ownership files and restores them on late failure.

A focused CI review identified the macos-14 deprecation; the workflow now uses macos-15 arm64/macOS Intel. Native Windows packaging verification remains pending.
No deferred style-only findings were reported. This review is code evidence, not a substitute for native Windows or clean-account acceptance.

## Artifacts

- `dist/QuickMD.app` — native arm64 onedir bundle, Python/runtime dependencies included.
- `dist/QuickMD-macOS-arm64.dmg` — development disk image, roughly 83 MiB compressed (exact size may vary by build).
- `dist/QuickMD-macOS-arm64.dmg.sha256`, `dist/SHA256SUMS` — SHA-256 of the local final package.
- `dist/licenses/` — runtime inventory, upstream license texts and Python license; corresponding notices also bundled inside the app.
- `build/dmg/install.sh`, `uninstall.sh`, `lifecycle.sh` — staged installer files, also included in the image.

Windows x64 EXE and macOS Intel DMG were **not built on this host**. Their native build scripts and CI matrix are implemented.

## Required before public release

Complete [MANUAL_TESTS.md](MANUAL_TESTS.md): Windows 10/11 Explorer selection behavior and actual counts, Intel/macOS 13 compatibility, Finder menu visibility, permission/notification behavior, install/update/uninstall on clean accounts without Python, and downloaded package behavior under default OS protections.

PowerShell/Inno compiler execution was not available locally. Those checks are configured on Windows CI but have not run remotely.
The current account's Finder menus, PATH and installed applications were left untouched. The supplied scripts can perform the installation when explicitly run.

Known limits are in the README: no OCR, approximate PDF layout, hard-link filesystem requirement, polling memory limit, possible temporary leftovers after forcible parent termination, legacy Windows selection cap and OS-dependent menu/notification permissions.
