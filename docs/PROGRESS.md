# Progress

- 2026-10-22: Empty repository, no upstream remote. macOS arm64 host, Python 3.12.10.
- Official documentation and live PyPI checked before implementation. MarkItDown 0.1.9 / PyInstaller 6.22.3 selected.
- Design follows supplied complete specification; implementation proceeds under the user's existing authorization.
- Task 1: complete — real four-format local conversion, subprocess limits, validation, duplicate detection and no-overwrite publication; automated tests.
- Task 2: complete — CLI, queue/global lock, Explorer registration, Automator workflow, native notification adapters, doctor and repair. Actual Automator execution confirmed on host.
- Task 3: complete for available host — PyInstaller app, Swift helper, arm64 DMG, dependency locks, license inventory and CI/scripts for native Windows/Intel builds. No remote CI or unavailable native builds claimed.
- Task 4: complete — Korean/English documentation, release registration procedure, exact validation evidence and manual acceptance matrix.
- Independent review: fixed malformed PATH deletion, broken-app removal and late-install rollback. Added regression coverage. Focused CI review updated retiring macOS runner.
- Focused release review: conditional Inno SignTool/SignedUninstaller added so certificate-backed builds also sign uninstallers and temporary setup copies; native verification configured in CI, not executed on this host.
- Additional regression: reject symlinked workflow Contents; observed failing test before fix, passing afterwards.
- Verification: 36 passed / 1 Windows-only skipped; Ruff and strict mypy (macOS + Windows target) clean. Frozen app converted PDF/DOCX/PPTX/XLSX; original/source safety tested.
- Ruling: use legacy Explorer Player verbs with request queue and document a 100-item cap; primary Windows 11 COM integration deferred per supplied MVP allowance. Cost: Show more options and mandatory real Explorer selection validation before release.
- Ruling: fail safely when output filesystem cannot create hard links. Cost: users of exFAT/some network shares must convert in a supported local folder.
- Ruling: do not change live user profile during development checks. Cost: Finder visibility and full install/update/removal acceptance remain manual release gates; no false production-ready claim.
