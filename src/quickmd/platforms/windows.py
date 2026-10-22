import ctypes
import importlib
import subprocess
import sys

from quickmd.validation import SUPPORTED

ROOT = r"Software\Classes\SystemFileAssociations"
VERB = "QuickMD.Convert"
AUMID = "QuickMD.Desktop"


def registry_entries(launcher: list[str]) -> list[tuple[str, str, str]]:
    command = subprocess.list2cmdline([*launcher, "shell-handler", "--"]) + ' "%1"'
    entries = []
    for extension in SUPPORTED:
        key = ROOT + "\\" + extension + "\\shell\\" + VERB
        entries.extend(
            [
                (key, "", "Markdown으로 변환"),
                (key, "MultiSelectModel", "Player"),
                (key, "Icon", launcher[0]),
                (key + "\\command", "", command),
            ]
        )
    return entries


def integrate(launcher: list[str]) -> None:
    if sys.platform != "win32":
        raise OSError("Windows required")
    winreg = importlib.import_module("winreg")
    for path, name, value in registry_entries(launcher):
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, path) as key:
            winreg.SetValueEx(key, name, 0, winreg.REG_SZ, value)
    ctypes.windll.shell32.SHChangeNotify(0x08000000, 0, None, None)


def unintegrate() -> None:
    if sys.platform != "win32":
        raise OSError("Windows required")
    winreg = importlib.import_module("winreg")
    for extension in SUPPORTED:
        key = ROOT + "\\" + extension + "\\shell\\" + VERB
        for path in (key + "\\command", key):
            try:
                winreg.DeleteKey(winreg.HKEY_CURRENT_USER, path)
            except FileNotFoundError:
                pass
    ctypes.windll.shell32.SHChangeNotify(0x08000000, 0, None, None)


def integration_status(launcher: list[str]) -> bool:
    if sys.platform != "win32":
        return False
    winreg = importlib.import_module("winreg")
    try:
        for path, name, value in registry_entries(launcher):
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, path) as key:
                if winreg.QueryValueEx(key, name)[0] != value:
                    return False
        return True
    except OSError:
        return False
