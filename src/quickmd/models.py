from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path


class Status(StrEnum):
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass(frozen=True)
class Result:
    source: Path
    status: Status
    output: Path | None = None
    message: str = ""
    error_type: str = ""


class ConversionError(Exception):
    """Only fixed, non-sensitive messages may cross the worker boundary."""
