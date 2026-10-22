import json
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

import psutil

from quickmd.models import ConversionError
from quickmd.runtime import command
from quickmd.validation import MAX_INPUT, check_container, validate

MAX_OUTPUT = 64 * 1024 * 1024


def run_bounded(
    argv: list[str],
    *,
    timeout: float = 120,
    memory_bytes: int = 2 * 1024**3,
) -> None:
    env = {**os.environ, "OMP_NUM_THREADS": "1", "OPENBLAS_NUM_THREADS": "1"}
    flags = 0x08000000 if sys.platform == "win32" else 0
    with subprocess.Popen(
        argv, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, env=env, creationflags=flags
    ) as process:
        start = time.monotonic()
        monitor = psutil.Process(process.pid)
        try:
            while process.poll() is None:
                if time.monotonic() - start > timeout:
                    raise ConversionError("변환 제한 시간을 초과했습니다 (120초 기본값).")
                try:
                    if monitor.memory_info().rss > memory_bytes:
                        raise ConversionError("변환 메모리 제한을 초과했습니다 (2 GiB).")
                except psutil.NoSuchProcess:
                    break
                time.sleep(0.05)
            if process.wait() != 0:
                raise ConversionError("변환 작업이 종료되었습니다. 손상/암호화 여부를 확인하세요.")
        finally:
            if process.poll() is None:
                process.kill()
            process.wait()


def convert_isolated(path: Path) -> str:
    """Snapshot bounded input; parse only in a separately supervised process."""
    validate(str(path))
    with tempfile.TemporaryDirectory(prefix="quickmd-") as directory:
        snapshot = Path(directory) / ("input" + path.suffix.lower())
        with path.open("rb") as source, snapshot.open("wb") as target:
            total = 0
            while chunk := source.read(1024 * 1024):
                total += len(chunk)
                if total > MAX_INPUT:
                    raise ConversionError("복사 도중 입력 파일 크기 제한을 초과했습니다.")
                target.write(chunk)
        response = Path(directory) / "result.json"
        run_bounded(command("_worker", str(snapshot), str(response)))
        if not response.is_file() or response.stat().st_size > MAX_OUTPUT:
            raise ConversionError("변환 결과가 없거나 출력 제한을 초과했습니다.")
        payload = json.loads(response.read_text(encoding="utf-8"))
        if payload.get("error"):
            raise ConversionError(payload["error"])
        markdown = payload.get("markdown")
        if not isinstance(markdown, str):
            raise ConversionError("변환 결과 형식이 올바르지 않습니다.")
        return markdown


def worker(source: Path, response: Path) -> int:
    # All model files are bundled. No plugins, HTTP, external processes or cloud adapters.
    import sys

    def deny_remote(event: str, args: tuple[object, ...]) -> None:
        if event in {"socket.connect", "socket.getaddrinfo", "subprocess.Popen", "os.system"}:
            raise PermissionError("Network and subprocesses are disabled in conversion workers")

    sys.addaudithook(deny_remote)
    try:
        import onnxruntime

        onnxruntime.disable_telemetry_events()
        from markitdown import MarkItDown
        from markitdown.converters import DocxConverter, PdfConverter, PptxConverter, XlsxConverter

        check_container(source)
        converter = MarkItDown(enable_builtins=False, enable_plugins=False)
        for adapter in (PdfConverter(), DocxConverter(), PptxConverter(), XlsxConverter()):  # type: ignore[no-untyped-call]
            converter.register_converter(adapter)
        result = converter.convert_local(source)
        text = result.markdown
        if len(text.encode("utf-8")) > MAX_OUTPUT // 2:
            raise ConversionError("출력 크기 제한 (32 MiB)을 초과했습니다.")
        payload = {"markdown": text}
    except Exception as exc:
        message = (
            str(exc)
            if isinstance(exc, ConversionError)
            else ("변환 실패: 손상/암호화 여부를 확인하세요. 스캔 PDF는 OCR이 필요합니다.")
        )
        payload = {"error": message}
    response.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
    return 0
