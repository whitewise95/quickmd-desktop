# QuickMD

Convert local PDF, DOCX, PPTX and XLSX files to Markdown from Windows Explorer or macOS Finder.
No account, API key, server, GUI or idle background process. Packaged installations include Python.

**0.1.0 is a development build.** No public release URL, WinGet package or Homebrew tap has been registered.
The current locally verified platform is macOS arm64. Windows, Intel, minimum OS versions, desktop menu visibility and notification delivery require the [manual matrix](MANUAL_TESTS.md).

## Install from source

There is no public installer download yet. These steps are for a development-preview build. Cloning the source does not install QuickMD by itself: you must install the build tools, build it on the target operating system, then run its installer. Open Terminal on macOS or PowerShell on Windows and follow the steps in order.

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

**If PowerShell says the file cannot be found:** the installer probably has not been built yet. A Git clone does not contain `dist\QuickMD-Setup-Windows-x64.exe`. Complete the Windows build steps above, then check:

```powershell
Test-Path .\dist\QuickMD-Setup-Windows-x64.exe
```

`True` means the installer exists. If it returns `False`, the Windows build steps above did not complete; resolve the error shown during the build first. **Python is not needed to run an installed QuickMD package, but there is no prebuilt public installer yet, so creating one from source requires Python 3.12 and Inno Setup 6.** Once a public Release is available, users can download and install it without Python.

No public GitHub Release, download helper, WinGet package or Homebrew tap is available yet. Development builds are unsigned and may show OS security warnings or be blocked. Do not bypass OS protections. See [validation](VALIDATION.md) for the tested platforms and limitations.

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
CI builds Windows x64, macOS Intel and arm64; tagged builds prepare a development draft release. Public installation is not supported yet.
See [releasing](RELEASING.md), [validation](VALIDATION.md), and [third-party notices](../THIRD_PARTY_NOTICES.md).
