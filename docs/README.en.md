# QuickMD

Convert local PDF, DOCX, PPTX and XLSX files to Markdown from Windows Explorer or macOS Finder.
No account, API key, server, GUI or idle background process. Packaged installations include Python.

**0.1.0 is a development preview.** The public GitHub Release includes CI-built and validated packages for Windows x64 and macOS Apple Silicon. WinGet and Homebrew are not registered. See the [validation record](VALIDATION.md) for current test coverage.

## Install

### Direct downloads (no Python required)

Download the latest public release for your operating system. Python and Git are not required to install or run the packaged app.

- [Windows x64 installer](https://github.com/whitewise95/quickmd-desktop/releases/latest/download/QuickMD-Setup-Windows-x64.exe)
- [macOS Apple Silicon disk image](https://github.com/whitewise95/quickmd-desktop/releases/latest/download/QuickMD-macOS-arm64.dmg) — open the DMG and follow the included installation instructions.
- [All versions and release notes](https://github.com/whitewise95/quickmd-desktop/releases)

The current version is [v0.1.0](https://github.com/whitewise95/quickmd-desktop/releases/tag/v0.1.0). A macOS Intel package is not available yet. The latest-download links will point to the newest public release as it is published.

### Build from source

Use these steps to build an installer yourself or to install on macOS. Cloning the source alone does not install QuickMD: you must install the build tools, build on the target operating system, then run its installer. Open Terminal on macOS or PowerShell on Windows and follow the steps in order.

### 1. Install the build tools and clone the repository

- **macOS:** Install Apple Command Line Tools with `xcode-select --install`, then install [Python 3.12](https://www.python.org/downloads/macos/). If you already use Homebrew, you can run `brew install python@3.12`.
- **Windows:** Install [Git](https://git-scm.com/download/win), [Python 3.12](https://www.python.org/downloads/windows/) (include the Python Launcher `py`), and [Inno Setup 6](https://jrsoftware.org/isdl.php).

From the folder where you want the project, clone it and enter the repository directory:

```bash
cd ~/Documents
git clone https://github.com/whitewise95/quickmd-desktop.git QuickMD
cd QuickMD
```

Run all following commands from this `QuickMD` folder. The `build/` and `dist/` folders are generated during the build and do not exist immediately after cloning.

### 2. Install dependencies and build

Build natively on the operating system and CPU where you plan to install QuickMD.

macOS:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install --require-hashes -r requirements-dev.lock
python -m pip install --no-deps --no-build-isolation -e .
python scripts/build.py
```

Windows PowerShell:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --require-hashes -r requirements-dev.lock
.\.venv\Scripts\python.exe -m pip install --no-deps --no-build-isolation -e .
.\.venv\Scripts\python.exe scripts\build.py
```

### 3. Install QuickMD

macOS, from the repository folder:

```bash
bash build/dmg/install.sh
```

The app is installed under `~/Library/Application Support/QuickMD/QuickMD.app`; the CLI link is `~/.local/bin/quickmd`. Open a new terminal and run `quickmd doctor`.

Windows: Open File Explorer, go to `QuickMD\dist`, double-click `QuickMD-Setup-Windows-x64.exe`, and follow the installer. It installs per-user under `%LOCALAPPDATA%\Programs\QuickMD` without administrator access. Open a new PowerShell window and run `quickmd doctor`.

**If PowerShell says the file cannot be found:** if you downloaded the artifact, extract the ZIP first and run `QuickMD-Setup-Windows-x64.exe` from the extracted folder. The `dist\QuickMD-Setup-Windows-x64.exe` path exists only after building from a cloned repository. A Git clone does not include the `dist` installer. If you built from source, check:

```powershell
Test-Path .\dist\QuickMD-Setup-Windows-x64.exe
```

`True` means the installer exists. If it returns `False`, the Windows build steps above did not complete; resolve the error shown during the build first. Python is not needed to run QuickMD or install the prebuilt Actions package. **Only building from source requires Python 3.12 and Inno Setup 6.**

No public GitHub Release, download helper, WinGet package or Homebrew tap is available yet. These development builds are not signed and notarized with official distribution certificates, so Windows SmartScreen or macOS Gatekeeper warnings may appear. See [validation](VALIDATION.md) for the tested platforms and limitations.

## Use

Select supported files and choose **Markdown으로 변환** (“Convert to Markdown”).
Windows 11 may require **Show more options**. Legacy registry verbs have a documented 100-item Player limit; unsupported mixed selections may hide the menu.
On macOS use Quick Actions or Services and enable the service in System Settings if needed.

```bash
quickmd convert report.pdf manual.docx slides.pptx data.xlsx
quickmd convert -- -filename.pdf
quickmd doctor
quickmd repair
quickmd unintegrate
quickmd integrate
quickmd uninstall
```

Output is UTF-8 beside the selected source. Existing output is never overwritten: numbered names are allocated atomically.
Batch processing continues after failures and deduplicates physical files. CLI exit codes: 0 success/skipped, 1 failure, 2 usage error.
`doctor` checks registration and performs a real PDF conversion; it cannot confirm actual Finder/Explorer visibility.
Notifications are best effort and require OS authorization. CLI `convert` prints results without notifications.

## Update and remove

Finish conversions, then rerun the newer official installer. No automatic update daemon.
Use `quickmd uninstall`; add `--purge-logs` to remove logs. Windows also supports Settings > Installed apps.
For macOS, even if the app is broken, run `bash "$HOME/Library/Application Support/QuickMD/uninstall.sh"`.
Converted Markdown and unrelated configuration are preserved. Edited or incomplete profile marker blocks are preserved.

## Limits and privacy

100 MiB input, 512 MiB/10,000 entries expanded OOXML, 120-second worker timeout, 32 MiB output.
Only one expensive worker per user. RSS is polled at 50ms with a 2 GiB termination threshold, not a kernel hard limit.
No plugins or network conversion. Python network/subprocess calls are blocked in the worker; ONNX telemetry is disabled.
This is not an OS sandbox for malicious native code. Logs contain status and timing, not content, source names or full paths.

Scanned PDFs need OCR, which is not included. Empty results fail. PDF visual layout is not reproduced exactly.
Atomic publication requires hard links (e.g. APFS/NTFS); FAT/exFAT and some network/cloud filesystems fail safely.
Forced termination may leave hidden temporary files, but existing output remains intact.

## Develop

Python 3.12; Xcode Command Line Tools on macOS, Inno Setup 6 on Windows. Build natively for each OS/CPU.

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install --require-hashes -r requirements-dev.lock
python -m pip install --no-deps --no-build-isolation -e .
python -m pytest -q
python -m ruff check src tests scripts
python -m mypy src/quickmd
python scripts/build.py
```

On Windows use `py -3.12` and `.venv\Scripts\python.exe` without activating the environment.
CI tests Windows x64, macOS Intel and Apple Silicon; tagged builds publish validated Windows and Apple Silicon packages with SHA256SUMS and GitHub build provenance. Intel remains withheld until its build passes.
See [releasing](RELEASING.md), [validation](VALIDATION.md), and [third-party notices](../THIRD_PARTY_NOTICES.md).
