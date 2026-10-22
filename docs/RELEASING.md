# Release procedure

No real repository URL, publisher identity, certificate or package-manager registration was supplied. These are operator inputs, not fabricated project defaults.

1. Create the actual public repository and configure its remote. Preserve MIT and third-party notices.
2. Run the full tests and [manual matrix](MANUAL_TESTS.md) on all supported targets, including no-Python systems.
3. Align `pyproject.toml`, `src/quickmd/__init__.py`, Inno version, PyInstaller bundle and notification-helper version. Add release notes.
4. Build natively with `python scripts/build.py`. Inspect `dist/licenses/inventory.json` and included license texts. No cloud/OCR extras should be present.
5. Configure signing below, build and validate Gatekeeper/Authenticode on a clean account.
6. Push a matching `vX.Y.Z` tag only when authorized. The workflow tests/builds all three targets, generates SHA256SUMS and GitHub build provenance, and creates a **draft** Release. This workspace has not pushed a tag or executed remote Actions.
7. Verify hashes, provenance and signatures. Complete the draft with downloads, real install commands, updates/removal instructions and known limitations before public publication.
8. Generate and validate package-manager submissions only after those URLs exist. Register packages; update README only after registration actually works.

## Signing inputs

macOS CI secrets: `APPLE_CERT_P12_BASE64`, `APPLE_CERT_PASSWORD`, `APPLE_SIGN_IDENTITY`, and for notarization `APPLE_ID`, `APPLE_TEAM_ID`, `APPLE_APP_PASSWORD`.
The optional script imports a temporary keychain, configures a notarytool profile, and passes the identity/profile via GITHUB_ENV. CI removes the temporary keychain afterwards.
Local builds may use an already-installed `APPLE_SIGN_IDENTITY` and `APPLE_NOTARY_PROFILE`.
The build signs nested code and app, signs the DMG, submits it to Apple and staples its ticket when configured.
Without secrets, ad-hoc signed development artifacts are produced and explicitly labeled. Missing notarization is never a public-release pass.

Windows CI secrets: `WINDOWS_CERT_PFX_BASE64` and `WINDOWS_CERT_PASSWORD`, with a certificate appropriate for the publisher's signing setup.
`windows-signing.ps1` imports into the ephemeral runner's CurrentUser store and selects the SDK signtool.
Local builds may set `WINDOWS_CERT_THUMBPRINT` and `SIGNTOOL` to an installed signing identity/tool.
The build signs CLI and shell executables before packaging, configures Inno SignTool with SignedUninstaller for the uninstaller and temporary setup copies, then signs the final installer. Signing-enabled CI also checks installed executable/uninstaller signatures. Hardware-backed/managed signing providers require adapting the signing step to the provider; do not export nonexportable keys.
No secrets means unsigned development installers, not a trusted public release.

## Package-manager files

`scripts/package_manifests.py` requires actual repository, publisher, WinGet ID, version and three trusted hashes.
It produces a singleton WinGet manifest and a Homebrew cask candidate. It does not register or publish either.

```text
python scripts/package_manifests.py --repository OWNER/REPO --package-id PUBLISHER.QuickMD --publisher "ACTUAL PUBLISHER" --version X.Y.Z --windows-sha SHA256 --arm-sha SHA256 --intel-sha SHA256
```

The uppercase arguments are placeholders and intentionally are not presented as working install commands.
Validate the generated WinGet YAML with `winget validate --manifest <directory>` on Windows, test the installer switches and submit to [microsoft/winget-pkgs](https://github.com/microsoft/winget-pkgs).
Validate/audit the cask with Homebrew in the actual tap, test install/update/uninstall and submit the registered tap or an eligible upstream cask.
See [WinGet manifests](https://learn.microsoft.com/en-us/windows/package-manager/package/manifest) and [Homebrew Cask cookbook](https://docs.brew.sh/Cask-Cookbook).
The generated cask uses the shipped per-user installer so Finder integration is installed too. It must be audited against current Homebrew policy before submission.

## Integrity and limitations

The trusted hash is a mandatory input to the standalone download helpers. A checksum from the same compromised source is not independent authentication.
Use Authenticode/Developer ID, notarization and [GitHub artifact attestations](https://docs.github.com/en/actions/security-for-github-actions/using-artifact-attestations) to verify publisher/build identity.
`gh attestation verify <artifact> --repo <actual-owner/repo>` is an optional maintainer verification command, not a required end-user dependency.
Public installers reject unsigned/unassessed downloaded artifacts. They never disable Gatekeeper or Windows execution policy.
Unsigned CI artifacts and draft releases must remain clearly marked development-only.
