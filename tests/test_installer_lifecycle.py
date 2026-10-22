import plistlib
import shlex
import subprocess
import sys
from pathlib import Path

import pytest

LIBRARY = Path(__file__).resolve().parents[1] / "packaging/macos/lifecycle.sh"
pytestmark = pytest.mark.skipif(sys.platform == "win32", reason="macOS shell lifecycle")


def run_function(name, *args):
    subprocess.run(
        [
            "/bin/bash",
            "-c",
            "set -e; source "
            + shlex.quote(str(LIBRARY))
            + "; "
            + shlex.join([name, *map(str, args)]),
        ],
        check=True,
    )


@pytest.mark.parametrize(
    "block",
    [
        '# >>> QuickMD PATH >>>\nexport PATH="$HOME/.local/bin:$PATH"\n',
        "# >>> QuickMD PATH >>>\nexport OTHER=keep\n# <<< QuickMD PATH <<<\n",
    ],
)
def test_uninstall_preserves_malformed_profile_blocks(tmp_path, block):
    profile = tmp_path / ".zprofile"
    text = "export BEFORE=keep\n" + block + "export AFTER=keep\n"
    profile.write_text(text)
    run_function("quickmd_remove_path_block", profile)
    assert profile.read_text() == text


def test_uninstall_removes_only_complete_owned_block(tmp_path):
    profile = tmp_path / ".zprofile"
    profile.write_text(
        'before\n# >>> QuickMD PATH >>>\nexport PATH="$HOME/.local/bin:$PATH"\n'
        "# <<< QuickMD PATH <<<\nafter\n"
    )
    run_function("quickmd_remove_path_block", profile)
    assert profile.read_text() == "before\nafter\n"


def test_removal_works_without_installed_executable(tmp_path):
    root = tmp_path / "Library/Application Support/QuickMD"
    root.mkdir(parents=True)
    (root / ".quickmd-install").write_text("owned")
    (root / "logs").mkdir()
    (root / "logs/quickmd.log").write_text("keep logs")
    workflow = tmp_path / "Library/Services/QuickMD — Markdown으로 변환.workflow"
    (workflow / "Contents").mkdir(parents=True)
    (workflow / "Contents/Info.plist").write_bytes(
        plistlib.dumps({"CFBundleIdentifier": "org.quickmd.convert"})
    )
    cli = tmp_path / ".local/bin/quickmd"
    cli.parent.mkdir(parents=True)
    cli.symlink_to(root / "QuickMD.app/Contents/MacOS/quickmd")
    document = tmp_path / "important.md"
    document.write_text("keep document")
    run_function("quickmd_remove_installation", tmp_path, "false")
    assert not workflow.exists()
    assert not cli.is_symlink()
    assert not (root / ".quickmd-install").exists()
    assert (root / "logs/quickmd.log").read_text() == "keep logs"
    assert document.read_text() == "keep document"


def test_failed_transaction_restores_existing_and_removes_created_files(tmp_path):
    existing = tmp_path / "profile"
    existing.write_text("original")
    created = tmp_path / "uninstall.sh"
    run_function("quickmd_snapshot_file", existing, tmp_path / "old")
    run_function("quickmd_snapshot_file", created, tmp_path / "new")
    existing.write_text("changed")
    created.write_text("created")
    run_function("quickmd_restore_file", existing, tmp_path / "old")
    run_function("quickmd_restore_file", created, tmp_path / "new")
    assert existing.read_text() == "original"
    assert not created.exists()
