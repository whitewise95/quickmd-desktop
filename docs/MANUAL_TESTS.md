# Desktop release acceptance matrix

Do not check an item merely because unit tests pass. Record OS version/build, CPU, package hash, signing status, date, tester, logs and result screenshots. Use a fresh account without Python or developer tools. **All rows below are pending unless an attached report says otherwise.**

| Target | Required systems |
|---|---|
| Windows | Windows 10 x64, Windows 11 x64; standard user |
| macOS | macOS 13 Intel and arm64, current macOS Intel and arm64 |

## Install/update/remove

- [ ] Install the correctly signed downloaded package using documented commands; no Python or admin prompt.
- [ ] Wrong OS/CPU, changed SHA-256 and invalid signature reject before installation.
- [ ] `quickmd doctor` works from a new terminal, engine test passes, registered command matches the installation.
- [ ] Reinstall twice; one menu, one PATH entry and one notification identity.
- [ ] Update from prior version; existing Markdown, other PATH entries and logs remain.
- [ ] Interrupt download, copy, menu registration and profile/PATH writing; retry/rollback remains recoverable.
- [ ] Remove/rename executable, then use official uninstall/repair procedure; registration and links are removed or repaired.
- [ ] Remove normally and with log purge; all unrelated app settings and user Markdown survive.
- [ ] Edited/incomplete shell profile marker blocks are preserved, never truncate the remaining profile.
- [ ] Reinstall after removal; menus and notifications work again.

## Explorer/Finder

- [ ] Context action appears only for supported types; record behavior for mixed/unsupported selections.
- [ ] Windows 10 classic and Windows 11 “Show more options” invoke the installed windowless launcher without a console flash.
- [ ] Windows selection counts 1, 2, 10, 50 and 100: count every output; 101+ behavior documented. Record actual process argv with a test launcher if any file is missing.
- [ ] macOS Quick Action receives every selected file (1, 2, 10, 50), including multiple folders. Test Services enablement and Finder relaunch if hidden.
- [ ] Korean, spaces, apostrophe, quotes where legal, shell metacharacters, leading hyphen, NFC/NFD, case variants, long paths and symlinks.
- [ ] Read-only input with writable output folder succeeds; read-only folder and disk full fail without partial Markdown.
- [ ] NTFS/APFS publication, SMB/network share, OneDrive/iCloud online/offline, exFAT unsupported hard-link behavior.
- [ ] Concurrent menus and duplicate selections preserve source and all existing output. No idle QuickMD daemon remains.
- [ ] Kill a worker/parent; existing files intact; identify temporary leftovers and pending requests. Verify next invocation drains queued work.

## Content/notifications

- [ ] Representative PDF, DOCX, PPTX and multi-sheet XLSX; check actual content, tables and Unicode.
- [ ] Empty/scanned, encrypted, corrupt, oversized and highly compressed input; failure messages and continued batch processing.
- [ ] Notification permission not requested/allowed/denied, Focus/Do Not Disturb and notifications disabled. Conversion still succeeds.
- [ ] Single-file result and partial-failure summaries, no notification flood for one batched selection.
- [ ] Signed downloaded DMG passes Gatekeeper on a clean Mac; no quarantine removal/security disabling.
- [ ] Authenticode installer/app signatures validate on clean Windows; record SmartScreen reputation separately.

Current automation executes source/frozen conversions, generated workflow execution, file races and installer helper operations. It does not substitute for these desktop observations.
