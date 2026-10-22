import os
import subprocess
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import pytest

from quickmd.conversion import convert_batch
from quickmd.storage import publish


def _publish_worker(arguments):
    path, text = arguments
    return str(publish(Path(path), text))


def test_independent_processes_publish_unique_complete_files(tmp_path):
    source = tmp_path / "parallel.pdf"
    with ProcessPoolExecutor(max_workers=4) as pool:
        outputs = list(pool.map(_publish_worker, [(str(source), str(i)) for i in range(12)]))
    assert len(set(outputs)) == 12
    assert {Path(p).read_text() for p in outputs} == {str(i) for i in range(12)}


@pytest.mark.parametrize("count", [1, 2, 10, 50])
def test_batch_size_and_failures(tmp_path, count):
    inputs = []
    for index in range(count):
        path = tmp_path / f"file {index}.pdf"
        path.write_bytes(b"%PDF-1.4\n")
        inputs.append(str(path))
    inputs.insert(0, str(tmp_path / "unsupported.exe"))
    results = convert_batch(inputs, engine=lambda _: "all good")
    assert sum(r.status == "success" for r in results) == count
    assert sum(r.status == "failed" for r in results) == 1
    assert len(list(tmp_path.glob("*.md"))) == count


def test_concurrent_shell_requests_are_all_drained(documents, tmp_path):
    environment = {**os.environ, "QUICKMD_DATA_DIR": str(tmp_path / "state")}
    children = [
        subprocess.Popen(
            [sys.executable, "-m", "quickmd", "shell-handler", "--", str(p)], env=environment
        )
        for p in documents
    ]
    assert all(p.wait(timeout=60) == 0 for p in children)
    assert len(list(tmp_path.glob("report*.md"))) == 4
    assert not list((tmp_path / "state/queue").glob("*.json"))


def test_logs_do_not_include_document_content_or_sensitive_paths(documents, tmp_path):
    environment = {**os.environ, "QUICKMD_DATA_DIR": str(tmp_path / "state")}
    result = subprocess.run(
        [sys.executable, "-m", "quickmd", "convert", str(documents[0])],
        env=environment,
        capture_output=True,
    )
    assert result.returncode == 0, f"stdout={result.stdout!r}\nstderr={result.stderr!r}"
    text = (tmp_path / "state/logs/quickmd.log").read_text()
    assert "QuickMD fixture text" not in text
    assert str(tmp_path) not in text
    assert "report.pdf" not in text
    assert "success" in text


def test_existing_output_symlink_is_not_followed(tmp_path):
    protected = tmp_path / "protected"
    protected.write_text("keep")
    (tmp_path / "source.md").symlink_to(protected)
    output = publish(tmp_path / "source.pdf", "new")
    assert output.name == "source (1).md"
    assert protected.read_text() == "keep"


@pytest.mark.skipif(sys.platform != "win32", reason="Native Windows registry test")
def test_native_registry_lifecycle(monkeypatch):
    import uuid
    import winreg

    from quickmd.platforms import windows

    root = "Software\\QuickMD.Tests." + uuid.uuid4().hex
    monkeypatch.setattr(windows, "ROOT", root)
    launcher = [sys.executable]
    try:
        windows.integrate(launcher)
        assert windows.integration_status(launcher)
        windows.integrate(launcher)
        windows.unintegrate()
        assert not windows.integration_status(launcher)
    finally:
        windows.unintegrate()
        for extension in (".pdf", ".docx", ".pptx", ".xlsx"):
            for suffix in (extension + "\\shell", extension):
                winreg.DeleteKey(winreg.HKEY_CURRENT_USER, root + "\\" + suffix)
        winreg.DeleteKey(winreg.HKEY_CURRENT_USER, root)
