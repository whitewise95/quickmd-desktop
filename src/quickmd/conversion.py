import logging
import time
from collections.abc import Callable, Iterable
from pathlib import Path

from quickmd.models import ConversionError, Result, Status
from quickmd.storage import publish
from quickmd.validation import validate


def convert_batch(
    paths: Iterable[str],
    *,
    engine: Callable[[Path], str] | None = None,
    seen: set[tuple[int, int]] | None = None,
) -> list[Result]:
    if engine is None:
        from quickmd.engine import convert_isolated

        engine = convert_isolated
    seen = seen if seen is not None else set()
    results: list[Result] = []
    for value in paths:
        source = Path(value)
        start = time.monotonic()
        logging.info(
            "conversion_start format=%s",
            source.suffix.lower()
            if source.suffix.lower() in (".pdf", ".docx", ".pptx", ".xlsx")
            else "other",
        )
        try:
            source = validate(value)
            info = source.stat()
            identity = (info.st_dev, info.st_ino)
            if identity in seen:
                results.append(Result(source, Status.SKIPPED, message="중복 요청"))
                continue
            seen.add(identity)
            markdown = engine(source)
            if not isinstance(markdown, str) or not markdown.replace("\x00", "").strip():
                raise ConversionError("추출된 텍스트가 없습니다. 스캔 PDF에는 OCR이 필요합니다.")
            if "\x00" in markdown:
                raise ConversionError("변환 결과에 잘못된 문자가 있습니다.")
            results.append(Result(source, Status.SUCCESS, output=publish(source, markdown)))
        except Exception as exc:
            if isinstance(exc, ConversionError):
                message = str(exc)
            elif isinstance(exc, PermissionError):
                message = "읽기/쓰기 권한을 확인하세요."
            elif isinstance(exc, OSError):
                message = "저장 실패: 공간, 권한 및 파일시스템의 하드 링크 지원을 확인하세요."
            else:
                message = "변환 실패: 손상 또는 암호화된 문서인지 확인하세요."
            results.append(
                Result(source, Status.FAILED, message=message, error_type=type(exc).__name__)
            )
        result = results[-1]
        logging.info(
            "conversion_end status=%s error=%s elapsed=%.3f",
            result.status,
            result.error_type,
            time.monotonic() - start,
        )
    return results
