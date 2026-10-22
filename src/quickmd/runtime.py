import os
import sys
from pathlib import Path


def command(*args: str) -> list[str]:
    if getattr(sys, "frozen", False):
        return [sys.executable, *args]
    return [sys.executable, "-m", "quickmd", *args]


def data_dir() -> Path:
    override = os.environ.get("QUICKMD_DATA_DIR")
    if override:
        return Path(override)
    if sys.platform == "win32":
        return Path(os.environ["LOCALAPPDATA"]) / "QuickMD" / "Data"
    return Path.home() / "Library" / "Application Support" / "QuickMD"


def shell_command() -> list[str]:
    if getattr(sys, "frozen", False):
        executable = Path(sys.executable).resolve()
        if sys.platform == "win32":
            executable = executable.with_name("quickmd-shell.exe")
        return [str(executable)]
    return command()
