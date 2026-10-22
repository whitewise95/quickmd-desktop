# Official-source research — 2026-10-22

Checked before implementation, with installed package source/signatures inspected afterwards.

| Decision | Evidence |
|---|---|
| MarkItDown local API, selective extras | [Microsoft repository](https://github.com/microsoft/markitdown), [releases](https://github.com/microsoft/markitdown/releases). Live PyPI reported 0.1.9; inspected installed `MarkItDown.__init__`, `convert_local(path, *, stream_info=None, ...)` and canonical `result.markdown`. |
| No remote fallback or general format converters | Actual 0.1.9 supports `enable_builtins=False`, `enable_plugins=False`, public `register_converter()`. Register only PDF/DOCX/PPTX/XLSX. |
| Legacy Windows Player verb | [Verb selection model](https://learn.microsoft.com/en-us/windows/win32/shell/how-to-employ-the-verb-selection-model): legacy Document 15, Player 100; COM Player unlimited. The setting is not proof all selected paths are passed in a single argv. Queue individual invocations; verify real Explorer separately. |
| Windows 11 classic menu initially | [Microsoft Explorer integration](https://learn.microsoft.com/en-us/windows/apps/desktop/modernize/integrate-packaged-app-with-file-explorer), [Windows developer explanation](https://blogs.windows.com/windowsdeveloper/2021/07/19/extending-the-context-menu-and-share-dialog-in-windows-11/): primary menu uses IExplorerCommand plus package identity/sparse package. Defer that COM extension. |
| Desktop toast identity | [Microsoft AUMID requirements](https://learn.microsoft.com/en-us/windows/win32/shell/enable-desktop-toast-with-appusermodelid): provide a Start Menu shortcut with AppUserModelID. Inno creates that shortcut; fixed PowerShell uses WinRT ToastNotificationManager and escaped XML text. |
| Finder Quick Action | [Apple Automator guide](https://support.apple.com/guide/automator/aut7cac58839/mac). Inspected installed Run Shell Script action Info.plist and Apple-provided workflow bundles; inputMethod=1 passes arguments. Actual generated workflow executed with `automator` on this host. |
| macOS notification permission | [Apple UserNotifications](https://developer.apple.com/documentation/usernotifications/unusernotificationcenter): separate helper app with persistent bundle ID, query settings and request permission when notifying. |
| PyInstaller native onedir bundle | [Usage](https://pyinstaller.org/en/stable/usage.html), [macOS signing](https://pyinstaller.org/en/stable/feature-notes.html). Live PyPI 6.22.3. No cross compilation; onedir avoids onefile unpacking per invocation. |
| Per-user Windows installer | [Inno privileges](https://jrsoftware.org/ishelp/topic_setup_privilegesrequired.htm), [stable AppId](https://jrsoftware.org/ishelp/topic_setup_appid.htm). `lowest`, HKCU and user PATH. |
| Signed Windows uninstall path | [Inno SignTool](https://jrsoftware.org/ishelp/topic_setup_signtool.htm), [SignedUninstaller](https://jrsoftware.org/ishelp/topic_setup_signeduninstaller.htm): configure at compile time to sign uninstallers and temporary setup copies; signing only the final installer is insufficient. |
| macOS distribution | [Apple signing policy](https://support.apple.com/guide/security/app-code-signing-process-sec3ad8e6e53/web): Developer ID and notarization for normal downloaded-app experience; never disable Gatekeeper. |
| Runner architectures | [GitHub runner reference](https://docs.github.com/en/actions/reference/runners/github-hosted-runners): windows-2022 x64; macos-15-intel x64; macos-15 arm64. Avoid macos-14 because [GitHub's removal notice](https://github.com/actions/runner-images/issues/13518) schedules retirement for 2026-11-02 and brownouts before that date. |

Dependency choice: newest NumPy/ONNX wheels observed required macOS 14. Pinned NumPy 1.26.4 (macOS 11 wheel), ONNX Runtime 1.20.1 (macOS 13 universal2 wheel), Magika 0.6.3 and pandas 2.2.3. These wheel tags inform compatibility but do not prove operation on macOS 13; that remains a release gate. Magika is MarkItDown's required file-type classifier, not an added OCR model.

Locked dependencies: `uv.lock`, `requirements.lock`, `requirements-dev.lock`. `uv lock` respects Python >=3.12,<3.13 and emits Windows conditional dependencies too. To regenerate with uv 0.13.5:

```bash
uv lock --python .venv/bin/python
uv export --no-dev --no-emit-project --format requirements-txt --output-file requirements.lock
uv export --extra dev --no-emit-project --format requirements-txt --output-file requirements-dev.lock
```

Review new licenses and rerun native tests/builds after changing locks. Keep source, PyInstaller, installer, helper and release-tag versions in sync.
