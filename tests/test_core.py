from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pytest

from quickmd.conversion import convert_batch
from quickmd.models import Status
from quickmd.storage import publish
from quickmd.validation import InputError, validate


def test_parallel_publication_never_overwrites(tmp_path):
    source = tmp_path / "한글 report.pdf"
    existing = tmp_path / "한글 report.md"
    existing.write_text("original")
    with ThreadPoolExecutor(max_workers=8) as pool:
        outputs = list(pool.map(lambda i: publish(source, f"result {i}"), range(20)))
    assert len(set(outputs)) == 20
    assert existing.read_text() == "original"
    assert {p.read_text() for p in outputs} == {f"result {i}" for i in range(20)}
    assert not list(tmp_path.glob(".quickmd-*.tmp"))


def test_failed_publication_cleans_temporary_file(tmp_path, monkeypatch):
    import os

    def denied(*args, **kwargs):
        raise PermissionError("denied")

    monkeypatch.setattr(os, "link", denied)
    with pytest.raises(PermissionError):
        publish(tmp_path / "file.pdf", "complete text")
    assert list(tmp_path.iterdir()) == []


@pytest.mark.parametrize("name", ["https://example.com/doc.pdf", "missing.pdf", "folder", "x.txt"])
def test_invalid_inputs_rejected(tmp_path, name):
    (tmp_path / "folder").mkdir()
    (tmp_path / "x.txt").write_text("text")
    with pytest.raises(InputError):
        validate(str(tmp_path / name) if "://" not in name else name)


def test_batch_continues_and_deduplicates(tmp_path):
    good = tmp_path / "한글 ' quote & $.pdf"
    bad = tmp_path / "bad.pdf"
    good.write_bytes(b"%PDF-1.4\ninput")
    bad.write_bytes(b"%PDF-1.4\ninput")

    def engine(path: Path) -> str:
        if path.name == "bad.pdf":
            raise ValueError("sensitive content should never be returned")
        return "# Hello"

    results = convert_batch([str(good), str(bad), str(good)], engine=engine)
    assert [r.status for r in results] == [Status.SUCCESS, Status.FAILED, Status.SKIPPED]
    assert results[0].output.read_text() == "# Hello"
    assert "sensitive" not in results[1].message
    assert good.read_bytes() == b"%PDF-1.4\ninput"


@pytest.mark.parametrize("text", ["", " \n\t", "\x00"])
def test_empty_result_is_failure(tmp_path, text):
    source = tmp_path / "scan.pdf"
    source.write_bytes(b"%PDF-1.4\n")
    result = convert_batch([str(source)], engine=lambda _: text)[0]
    assert result.status == Status.FAILED
    assert not source.with_suffix(".md").exists()


def test_symlink_uses_selected_folder_and_deduplicates(tmp_path):
    source = tmp_path / "real.pdf"
    source.write_bytes(b"%PDF-1.4\n")
    alias = tmp_path / "alias.pdf"
    alias.symlink_to(source)
    results = convert_batch([str(alias), str(source)], engine=lambda _: "markdown")
    assert results[0].output == tmp_path / "alias.md"
    assert results[1].status == Status.SKIPPED


def test_input_size_limit(tmp_path):
    source = tmp_path / "large.pdf"
    source.write_bytes(b"%PDF-1.4\nmore")
    with pytest.raises(InputError):
        validate(str(source), max_bytes=4)
