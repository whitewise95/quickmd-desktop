"""Build on the target OS; optional signing uses the existing CI signing identity."""

import hashlib
import os
import platform
import plistlib
import shutil
import subprocess
import sys
from pathlib import Path

from licenses import export

ROOT = Path(__file__).resolve().parents[1]


def run(*args: str) -> None:
    subprocess.run(args, cwd=ROOT, check=True)


def main() -> None:
    os.environ.setdefault("PYINSTALLER_CONFIG_DIR", str(ROOT / "build/pyinstaller-cache"))
    export(ROOT / "build/licenses")
    run(sys.executable, "-m", "PyInstaller", "--clean", "--noconfirm", "packaging/quickmd.spec")
    dist = ROOT / "dist"
    if sys.platform == "darwin":
        helper = dist / "QuickMD.app/Contents/Helpers/QuickMDNotify.app/Contents"
        (helper / "MacOS").mkdir(parents=True, exist_ok=True)
        (helper / "Info.plist").write_bytes(
            plistlib.dumps(
                {
                    "CFBundleIdentifier": "org.quickmd.notify",
                    "CFBundleName": "QuickMD",
                    "CFBundleExecutable": "QuickMDNotify",
                    "CFBundlePackageType": "APPL",
                    "CFBundleVersion": "1",
                    "CFBundleShortVersionString": "0.1.0",
                    "LSUIElement": True,
                    "LSMinimumSystemVersion": "13.0",
                }
            )
        )
        cache = ROOT / "build/swift-cache"
        cache.mkdir(parents=True, exist_ok=True)
        run(
            "xcrun",
            "swiftc",
            "-module-cache-path",
            str(cache),
            "-target",
            f"{platform.machine()}-apple-macos13.0",
            "packaging/macos/Notify.swift",
            "-o",
            str(helper / "MacOS/QuickMDNotify"),
        )
        identity = os.environ.get("APPLE_SIGN_IDENTITY", "-")
        for bundle in (helper.parent, dist / "QuickMD.app"):
            run(
                "codesign",
                "--force",
                "--deep",
                "--options",
                "runtime",
                "--sign",
                identity,
                "--entitlements",
                "packaging/macos/entitlements.plist",
                str(bundle),
            )
        run("codesign", "--verify", "--deep", "--strict", str(dist / "QuickMD.app"))
        run(str(dist / "QuickMD.app/Contents/MacOS/quickmd"), "doctor", "--no-integration")
        stage = ROOT / "build/dmg"
        if stage.exists():
            shutil.rmtree(stage)
        stage.mkdir(parents=True)
        run("ditto", str(dist / "QuickMD.app"), str(stage / "QuickMD.app"))
        for source in ("install.sh", "uninstall.sh", "lifecycle.sh"):
            shutil.copy2(ROOT / "packaging/macos" / source, stage / source)
        shutil.copy2(ROOT / "README.md", stage / "README.md")
        shutil.copytree(ROOT / "docs", stage / "docs")
        for notice in ("LICENSE", "THIRD_PARTY_NOTICES.md"):
            shutil.copy2(ROOT / notice, stage / notice)
        suffix = "arm64" if platform.machine() == "arm64" else "x64"
        artifact = dist / f"QuickMD-macOS-{suffix}.dmg"
        artifact.unlink(missing_ok=True)
        run(
            "hdiutil",
            "create",
            "-volname",
            "QuickMD",
            "-srcfolder",
            str(stage),
            "-format",
            "UDZO",
            str(artifact),
        )
        if identity != "-":
            run("codesign", "--force", "--sign", identity, str(artifact))
        if os.environ.get("APPLE_NOTARY_PROFILE"):
            run(
                "xcrun",
                "notarytool",
                "submit",
                str(artifact),
                "--keychain-profile",
                os.environ["APPLE_NOTARY_PROFILE"],
                "--wait",
            )
            run("xcrun", "stapler", "staple", str(artifact))
        elif identity == "-":
            print("DEVELOPMENT artifact: ad-hoc signed; not notarized; not a public release.")
    elif sys.platform == "win32":
        run(str(dist / "QuickMD/quickmd.exe"), "doctor", "--no-integration")
        if os.environ.get("WINDOWS_CERT_THUMBPRINT"):
            for binary in ("quickmd.exe", "quickmd-shell.exe"):
                sign_windows(dist / "QuickMD" / binary)
        compiler = os.environ.get("ISCC", r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe")
        compiler_args = [compiler]
        if os.environ.get("WINDOWS_CERT_THUMBPRINT"):
            tool = os.environ.get("SIGNTOOL", "signtool").replace("$", "$$")
            thumbprint = os.environ["WINDOWS_CERT_THUMBPRINT"]
            signing = (
                f"$q{tool}$q sign /sha1 {thumbprint} /fd SHA256 "
                "/tr http://timestamp.digicert.com /td SHA256 $f"
            )
            compiler_args.extend(["/DSignedBuild=1", "/SQuickMD=" + signing])
        run(*compiler_args, "packaging/windows/QuickMD.iss")
        artifact = dist / "QuickMD-Setup-Windows-x64.exe"
        if os.environ.get("WINDOWS_CERT_THUMBPRINT"):
            sign_windows(artifact)
        else:
            print("DEVELOPMENT artifact: unsigned Windows installer.")
    else:
        raise SystemExit("Build on Windows or macOS")
    shutil.copytree(ROOT / "build/licenses", dist / "licenses", dirs_exist_ok=True)
    with artifact.open("rb") as stream:
        digest = hashlib.file_digest(stream, "sha256").hexdigest()
    (dist / (artifact.name + ".sha256")).write_text(f"{digest}  {artifact.name}\n")
    checksums = []
    for package in sorted([*dist.glob("*.exe"), *dist.glob("*.dmg")]):
        with package.open("rb") as stream:
            package_digest = hashlib.file_digest(stream, "sha256").hexdigest()
        checksums.append(f"{package_digest}  {package.name}\n")
    (dist / "SHA256SUMS").write_text("".join(checksums), encoding="utf-8")


def sign_windows(path: Path) -> None:
    run(
        os.environ.get("SIGNTOOL", "signtool"),
        "sign",
        "/sha1",
        os.environ["WINDOWS_CERT_THUMBPRINT"],
        "/fd",
        "SHA256",
        "/tr",
        "http://timestamp.digicert.com",
        "/td",
        "SHA256",
        str(path),
    )


if __name__ == "__main__":
    main()
