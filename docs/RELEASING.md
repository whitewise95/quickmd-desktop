# Release procedure

QuickMD releases are development previews. The build pipeline does not require extra credentials, but downloaded packages may show OS security warnings or be blocked. Do not describe these packages as ready for general users, and do not bypass OS protections.

1. Keep the real repository and publisher details in the project. Preserve the MIT and third-party notices.
2. Complete the [manual acceptance matrix](MANUAL_TESTS.md) before claiming support for a platform, including clean systems without Python. Current Release assets are Windows x64 and macOS Apple Silicon; macOS Intel remains under CI validation and is withheld until its build passes.
3. Align `pyproject.toml`, `src/quickmd/__init__.py`, Inno Setup, PyInstaller and notification-helper versions. Update the release notes.
4. Build natively with `python scripts/build.py`. Inspect `dist/licenses/inventory.json` and the included license texts. Do not include cloud or OCR extras.
5. Push a matching `vX.Y.Z` tag after checks pass. CI tests Windows x64, macOS Apple Silicon and macOS Intel. The release job publishes only the Windows and Apple Silicon artifacts, with SHA256SUMS and GitHub build provenance; the Intel package is withheld until its native build and conversion check pass. CI creates a draft Release; publish it from GitHub Releases after reviewing the assets and notes.
6. Check the files, checksums, provenance, installation behavior and known limitations. Keep the Release clearly labeled as a development preview.
7. Prepare package-manager submissions only after their URLs and package identifiers exist. Register each package before advertising its install command.

## Package-manager files

`scripts/package_manifests.py` requires the real repository, publisher, WinGet ID, version and three trusted hashes. It produces a singleton WinGet manifest and a Homebrew cask candidate. It does not register or publish either.

```text
python scripts/package_manifests.py --repository OWNER/REPO --package-id PUBLISHER.QuickMD --publisher "ACTUAL PUBLISHER" --version X.Y.Z --windows-sha SHA256 --arm-sha SHA256 --intel-sha SHA256
```

The uppercase arguments are placeholders. Validate the generated WinGet YAML with `winget validate --manifest <directory>` on Windows, test the installer switches and submit to [microsoft/winget-pkgs](https://github.com/microsoft/winget-pkgs).
Validate and audit the cask with Homebrew in the actual tap, test install/update/uninstall and submit an eligible package. The generated cask uses the shipped per-user installer so Finder integration is installed too. It must be audited against current Homebrew policy before submission.

## Integrity and limitations

A SHA-256 value detects changes only when compared with a value obtained through a trusted, independent channel. A checksum downloaded beside the package does not by itself prove who published it. GitHub artifact provenance records which source and workflow produced the build; maintainer verification can use `gh attestation verify <artifact> --repo <actual-owner/repo>`.

The download helpers enforce OS trust checks and never disable Gatekeeper or Windows execution policy. Current development packages may not pass those checks, so use them only for development evaluation. WinGet and Homebrew availability must not be claimed until registration is complete.
