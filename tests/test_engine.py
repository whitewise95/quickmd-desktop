import hashlib
import sys
import zipfile

import pytest

from quickmd.conversion import convert_batch
from quickmd.engine import convert_isolated, run_bounded
from quickmd.models import ConversionError, Status
from quickmd.validation import InputError, check_container


def test_real_four_formats_preserve_originals(documents):
    before = [hashlib.sha256(p.read_bytes()).hexdigest() for p in documents]
    results = convert_batch(map(str, documents))
    assert all(r.status == Status.SUCCESS for r in results), results
    assert len({r.output for r in results}) == 4
    for result in results:
        assert "QuickMD fixture text" in result.output.read_text()
    assert [hashlib.sha256(p.read_bytes()).hexdigest() for p in documents] == before


def test_worker_timeout_kills_child():
    with pytest.raises(ConversionError, match="시간"):
        run_bounded([sys.executable, "-c", "import time; time.sleep(30)"], timeout=0.1)


def test_worker_memory_limit():
    with pytest.raises(ConversionError, match="메모리"):
        run_bounded(
            [sys.executable, "-c", "import time; x=bytearray(40_000_000); time.sleep(30)"],
            memory_bytes=20_000_000,
        )


def test_corrupt_and_encrypted_pdf_fail(documents, tmp_path):
    from pypdf import PdfReader, PdfWriter

    writer = PdfWriter()
    writer.append_pages_from_reader(PdfReader(documents[0]))
    writer.encrypt("password")
    encrypted = tmp_path / "encrypted.pdf"
    writer.write(encrypted)
    corrupt = tmp_path / "corrupt.pdf"
    corrupt.write_bytes(b"%PDF-1.7\nbroken")
    for path in (encrypted, corrupt):
        with pytest.raises(ConversionError):
            convert_isolated(path)
        assert not path.with_suffix(".md").exists()


def test_mismatched_office_container_rejected(tmp_path):
    path = tmp_path / "wrong.docx"
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr("xl/workbook.xml", "<test/>")
    with pytest.raises(InputError):
        check_container(path)
