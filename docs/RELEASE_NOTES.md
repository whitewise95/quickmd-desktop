# QuickMD development release

Local PDF, DOCX, PPTX and XLSX conversion; safe numbered output; sequential batches;
Explorer classic context menu and Finder Quick Action; notifications, doctor and repair;
per-user installers/uninstallers, native packages and dependency lock files.

This is a development preview. Complete `docs/MANUAL_TESTS.md` before describing it as ready for general users.
Downloaded development packages may trigger OS security warnings or be blocked. Do not bypass OS protections.

Download the artifact for Windows x64, macOS arm64 or macOS Intel. Verify SHA256SUMS,
GitHub provenance. Follow the README's development installation notes.
For updates rerun the newer installer after conversions finish. Remove with
`quickmd uninstall` or the documented official OS procedure; converted Markdown is preserved.

Known limitations: no OCR; PDF layout is approximate; Windows 11 uses “Show more options”;
legacy Explorer menu selection limit 100; notifications depend on OS permission;
hard-link-capable output filesystem required; minimum OS and actual desktop behavior
must have recorded acceptance tests. WinGet and Homebrew availability must not be claimed until registered.
