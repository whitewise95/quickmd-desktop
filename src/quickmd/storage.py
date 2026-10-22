import os
import tempfile
from pathlib import Path


def publish(source: Path, markdown: str) -> Path:
    """Publish a complete file without ever replacing an existing directory entry."""
    fd, name = tempfile.mkstemp(prefix=".quickmd-", suffix=".tmp", dir=source.parent)
    temporary = Path(name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            stream.write(markdown)
            stream.flush()
            os.fsync(stream.fileno())
        for number in range(100_000):
            suffix = f" ({number})" if number else ""
            output = source.with_name(f"{source.stem}{suffix}.md")
            try:
                os.link(temporary, output)
            except FileExistsError:
                continue
            return output
        raise FileExistsError("Too many output name collisions")
    finally:
        temporary.unlink(missing_ok=True)
