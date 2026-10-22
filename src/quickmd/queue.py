import json
import os
import time
import uuid
from collections.abc import Callable
from pathlib import Path

from quickmd.conversion import convert_batch
from quickmd.models import Result, Status


def enqueue(paths: list[str], spool: Path) -> None:
    spool.mkdir(parents=True, exist_ok=True, mode=0o700)
    token = uuid.uuid4().hex
    temporary = spool / f"{token}.tmp"
    try:
        with temporary.open("x", encoding="utf-8") as stream:
            json.dump([os.path.abspath(p) for p in paths], stream, ensure_ascii=False)
            stream.flush()
            os.fsync(stream.fileno())
        temporary.rename(spool / f"{token}.json")
    finally:
        temporary.unlink(missing_ok=True)


def drain(
    spool: Path,
    *,
    engine: Callable[[Path], str] | None = None,
    quiet_seconds: float = 0.5,
) -> list[Result]:
    """Caller holds the global lock. Every enqueuer waits for it, avoiding a lost wakeup."""
    results: list[Result] = []
    seen: set[tuple[int, int]] = set()
    while True:
        time.sleep(quiet_seconds)
        requests = sorted(spool.glob("*.json"))
        if not requests:
            break
        for request in requests:
            try:
                if request.stat().st_size > 1024 * 1024:
                    raise ValueError("oversized request")
                paths = json.loads(request.read_text(encoding="utf-8"))
                if not isinstance(paths, list) or not all(isinstance(p, str) for p in paths):
                    raise ValueError("invalid request")
                results.extend(convert_batch(paths, engine=engine, seen=seen))
            except (ValueError, OSError):
                results.append(
                    Result(Path("request"), Status.FAILED, message="변환 요청을 읽을 수 없습니다.")
                )
            request.unlink(missing_ok=True)
    return results
