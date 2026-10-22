# QuickMD development release

Local PDF, DOCX, PPTX and XLSX conversion; safe numbered output; sequential batches;
Explorer classic context menu and Finder Quick Action; notifications, doctor and repair;
per-user installers/uninstallers, native packages and dependency lock files.

**Release operator:** replace this development notice only after completing
`docs/MANUAL_TESTS.md`. Confirm the tag matches the packaged version and record signing/notarization status for each artifact.
Unsigned or unnotarized artifacts are for development, not verified public installation.

Download the artifact for Windows x64, macOS arm64 or macOS Intel. Verify SHA256SUMS,
GitHub provenance and OS signatures. Follow the README's installer commands.
For updates rerun the newer installer after conversions finish. Remove with
`quickmd uninstall` or the documented official OS procedure; converted Markdown is preserved.

Known limitations: no OCR; PDF layout is approximate; Windows 11 uses “Show more options”;
legacy Explorer menu selection limit 100; notifications depend on OS permission;
hard-link-capable output filesystem required; minimum OS and actual desktop behavior
must have recorded acceptance tests. WinGet and Homebrew availability must not be claimed until registered.
