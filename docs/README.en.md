# QuickMD

Convert local PDF, DOCX, PPTX and XLSX files to Markdown from Windows Explorer or macOS Finder.
No account, API key, server, GUI or idle background process. Packaged installations include Python.

**0.1.0 is a development preview.** The public GitHub Release includes CI-built and validated packages for Windows x64 and macOS Apple Silicon. WinGet and Homebrew are not registered. See the [validation record](VALIDATION.md) for current test coverage.

## Install

### Windows 10/11 (x64)

[Download the installer](https://github.com/whitewise95/quickmd-desktop/releases/latest/download/QuickMD-Setup-Windows-x64.exe), double-click it, and follow the prompts. Python and Git are not required. If SmartScreen warns you, do not force it to run. To build it yourself, follow the Windows source steps below. Local builds may still be blocked by security settings.

### Build from source (macOS and Windows)

You need Git and Python 3.12. On Mac, also install Apple Command Line Tools; on Windows, install [Inno Setup 6](https://jrsoftware.org/isdl.php).

In Terminal (macOS) or PowerShell (Windows), clone the repository:

```bash
cd ~/Documents
git clone https://github.com/whitewise95/quickmd-desktop.git QuickMD
cd QuickMD
```

**macOS** — If needed, install Apple Command Line Tools with `xcode-select --install`. From the repository folder:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install --require-hashes -r requirements-dev.lock
python -m pip install --no-deps --no-build-isolation -e .
python scripts/build.py
bash build/dmg/install.sh
```

**Windows PowerShell** — From the repository folder:

```powershell
py -3.12 -m venv .venv
.\\.venv\\Scripts\\python.exe -m pip install --require-hashes -r requirements-dev.lock
.\\.venv\\Scripts\\python.exe -m pip install --no-deps --no-build-isolation -e .
.\\.venv\\Scripts\\python.exe scripts\\build.py
.\\dist\\QuickMD-Setup-Windows-x64.exe
```

Build from source if you want to inspect the code yourself. It does not replace signing or notarization, so security warnings are not guaranteed to disappear. Do not bypass warnings or disable security features.

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
