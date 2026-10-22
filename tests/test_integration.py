import plistlib
import subprocess
import sys

import pytest

from quickmd.platforms.macos import install_workflow, remove_workflow, workflow_status
from quickmd.platforms.windows import registry_entries
from quickmd.queue import drain, enqueue


@pytest.mark.skipif(sys.platform == "win32", reason="POSIX shell contract")
def test_workflow_forwards_all_paths_without_shell_interpretation(tmp_path):
    recorder = tmp_path / "record args.py"
    output = tmp_path / "args.txt"
    recorder.write_text(
        "import sys,json; from pathlib import Path; "
        "Path(sys.argv[1]).write_text(json.dumps(sys.argv[2:]))"
    )
    launcher = [sys.executable, str(recorder), str(output)]
    workflow = install_workflow(launcher, tmp_path / "Services")
    payload = plistlib.loads((workflow / "Contents/document.wflow").read_bytes())
    action = payload["actions"][0]["action"]
    script = action["ActionParameters"]["COMMAND_STRING"]
    paths = ["/tmp/한글 ' $x.pdf", "/tmp/$(touch PWNED).docx", "-test.pdf"]
    subprocess.run(["/bin/bash", "-c", script, "quickmd", *paths], check=True)
    import json

    assert json.loads(output.read_text()) == ["shell-handler", "--", *paths]
    assert action["ActionParameters"]["inputMethod"] == 1
    assert workflow_status(launcher, tmp_path / "Services")
    install_workflow(launcher, tmp_path / "Services")
    assert len(list((tmp_path / "Services").iterdir())) == 1
    remove_workflow(tmp_path / "Services")
    assert not workflow.exists()


def test_workflow_preserves_unrelated_bundle(tmp_path):
    services = tmp_path / "Services"
    services.mkdir()
    other = services / "Other.workflow"
    other.mkdir()
    install_workflow(["/tmp/quickmd"], services)
    remove_workflow(services)
    assert other.is_dir()


def test_workflow_refuses_redirected_contents(tmp_path):
    from quickmd.platforms.macos import WORKFLOW

    services = tmp_path / "Services"
    bundle = services / WORKFLOW
    bundle.mkdir(parents=True)
    outside = tmp_path / "other-app"
    outside.mkdir()
    info = plistlib.dumps({"CFBundleIdentifier": "org.quickmd.convert"})
    (outside / "Info.plist").write_bytes(info)
    (bundle / "Contents").symlink_to(outside, target_is_directory=True)
    with pytest.raises(OSError):
        install_workflow(["/tmp/quickmd"], services)
    assert (outside / "Info.plist").read_bytes() == info


def test_windows_registration_quotes_paths_and_limits_extensions():
    entries = registry_entries([r"C:\Users\한글 User\QuickMD\quickmd-shell.exe"])
    commands = [v for key, name, v in entries if key.endswith("\\command")]
    assert len(commands) == 4
    assert all(v.endswith(' shell-handler -- "%1"') for v in commands)
    assert all(v.startswith('"C:\\Users\\한글 User') for v in commands)
    assert len([v for _, name, v in entries if name == "MultiSelectModel" and v == "Player"]) == 4
    assert not any("\\*\\" in key for key, _, _ in entries)


def test_queue_keeps_every_request_and_deduplicates_batch(tmp_path):
    source = tmp_path / "input.pdf"
    source.write_bytes(b"%PDF-1.4\n")
    spool = tmp_path / "queue"
    for _ in range(10):
        enqueue([str(source)], spool)
    results = drain(spool, engine=lambda _: "converted", quiet_seconds=0)
    assert len([r for r in results if r.status == "success"]) == 1
    assert not list(spool.glob("*.json"))
    assert source.with_suffix(".md").read_text() == "converted"


def test_cli_leading_hyphen_and_mixed_failures(documents, tmp_path):
    from quickmd.cli import main

    assert main(["convert", "--", str(documents[0]), str(tmp_path / "missing.pdf")]) == 1
    assert documents[0].with_suffix(".md").exists()
