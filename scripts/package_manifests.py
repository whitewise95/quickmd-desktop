"""Generate submission templates after actual release identity is known."""

import argparse
import json
import re
from pathlib import Path


def generate(
    repository: str,
    package_id: str,
    publisher: str,
    version: str,
    windows_sha: str,
    arm_sha: str,
    intel_sha: str,
    output: Path,
) -> None:
    if not re.fullmatch(r"[\w.-]+/[\w.-]+", repository):
        raise ValueError("Expected actual GitHub OWNER/REPO")
    if not re.fullmatch(r"[A-Za-z0-9]+(?:\.[A-Za-z0-9]+)+", package_id):
        raise ValueError("Expected actual WinGet publisher.package identifier")
    if not re.fullmatch(r"\d+\.\d+\.\d+", version):
        raise ValueError("Expected semantic release version")
    if not all(
        re.fullmatch(r"[a-fA-F0-9]{64}", digest) for digest in (windows_sha, arm_sha, intel_sha)
    ):
        raise ValueError("All three trusted SHA-256 values are required")
    base = f"https://github.com/{repository}"
    download = f"{base}/releases/download/v{version}"
    manifest = {
        "PackageIdentifier": package_id,
        "PackageVersion": version,
        "PackageLocale": "en-US",
        "Publisher": publisher,
        "PackageName": "QuickMD",
        "License": "MIT",
        "ShortDescription": "Local right-click Markdown conversion",
        "PackageUrl": base,
        "InstallerType": "inno",
        "Scope": "user",
        "Installers": [
            {
                "Architecture": "x64",
                "InstallerUrl": f"{download}/QuickMD-Setup-Windows-x64.exe",
                "InstallerSha256": windows_sha.upper(),
            }
        ],
        "ManifestType": "singleton",
        "ManifestVersion": "1.12.0",
    }
    output.mkdir(parents=True, exist_ok=True)
    (output / f"{package_id}.yaml").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    cask = f'''cask "quickmd" do
  arch arm: "arm64", intel: "x64"
  version "{version}"
  sha256 arm: "{arm_sha.lower()}", intel: "{intel_sha.lower()}"
  url "{base}/releases/download/v#{{version}}/QuickMD-macOS-#{{arch}}.dmg"
  name "QuickMD"
  desc "Local right-click Markdown conversion"
  homepage "{base}"
  depends_on macos: ">= :ventura"
  installer script: {{ executable: "#{{staged_path}}/install.sh", sudo: false }}
  uninstall script: {{ executable: "#{{Dir.home}}/Library/Application Support/QuickMD/uninstall.sh", sudo: false }}
end
'''
    (output / "quickmd.rb").write_text(cask, encoding="utf-8")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    for option in (
        "repository",
        "package-id",
        "publisher",
        "version",
        "windows-sha",
        "arm-sha",
        "intel-sha",
    ):
        parser.add_argument("--" + option, required=True)
    parser.add_argument("--output", type=Path, default=Path("build/manifests"))
    generate(**vars(parser.parse_args()))
