import os
import stat
import zipfile
from pathlib import Path

from quickmd.models import ConversionError

SUPPORTED = (".pdf", ".docx", ".pptx", ".xlsx")
MAX_INPUT = 100 * 1024 * 1024
MAX_EXPANDED = 512 * 1024 * 1024


class InputError(ConversionError):
    pass


def validate(value: str, *, max_bytes: int = MAX_INPUT) -> Path:
    if "://" in value or "\x00" in value:
        raise InputError("로컬 파일 경로만 사용할 수 있습니다.")
    path = Path(os.path.abspath(os.path.expanduser(value)))
    if path.suffix.lower() not in SUPPORTED:
        raise InputError("지원 형식: PDF, DOCX, PPTX, XLSX")
    try:
        info = path.stat()
        if not stat.S_ISREG(info.st_mode):
            raise InputError("일반 파일만 변환할 수 있습니다.")
        if info.st_size > max_bytes:
            raise InputError("파일 크기가 100 MiB 제한을 초과했습니다.")
        if info.st_size == 0:
            raise InputError("입력 파일이 비어 있습니다.")
    except OSError as exc:
        raise InputError("파일이 없거나 접근할 수 없습니다. 동기화와 권한을 확인하세요.") from exc
    return path


def check_container(path: Path) -> None:
    if path.suffix.lower() == ".pdf":
        with path.open("rb") as stream:
            if b"%PDF-" not in stream.read(1024):
                raise InputError("PDF 형식이 올바르지 않거나 손상되었습니다.")
        return
    try:
        with zipfile.ZipFile(path) as archive:
            members = archive.infolist()
            if len(members) > 10_000 or sum(m.file_size for m in members) > MAX_EXPANDED:
                raise InputError("압축 해제 크기 또는 항목 수가 안전 제한을 초과했습니다.")
            if any(m.flag_bits & 1 for m in members):
                raise InputError("암호화된 Office 문서는 지원하지 않습니다.")
            expected = {
                ".docx": "word/document.xml",
                ".pptx": "ppt/presentation.xml",
                ".xlsx": "xl/workbook.xml",
            }[path.suffix.lower()]
            if expected not in archive.namelist():
                raise InputError("확장자와 문서 형식이 일치하지 않습니다.")
    except zipfile.BadZipFile as exc:
        raise InputError("Office 문서가 손상되었거나 암호화되어 있습니다.") from exc
