import logging
import os
import subprocess
import sys
from pathlib import Path

from quickmd.models import Result, Status

WINDOWS_SCRIPT = r"""
$ErrorActionPreference = 'Stop'
[Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType=WindowsRuntime] > $null
[Windows.Data.Xml.Dom.XmlDocument, Windows.Data.Xml.Dom.XmlDocument, ContentType=WindowsRuntime] > $null
$notifier = [Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier('QuickMD.Desktop')
if ($env:QUICKMD_NOTIFY_STATUS -eq '1') { Write-Output $notifier.Setting; exit 0 }
$xml = [Windows.Data.Xml.Dom.XmlDocument]::new()
$title = [System.Security.SecurityElement]::Escape($env:QUICKMD_NOTIFY_TITLE)
$body = [System.Security.SecurityElement]::Escape($env:QUICKMD_NOTIFY_BODY)
$xml.LoadXml("<toast><visual><binding template='ToastGeneric'><text>$title</text><text>$body</text></binding></visual></toast>")
$toast = [Windows.UI.Notifications.ToastNotification]::new($xml)
$notifier.Show($toast)
"""


def _helper() -> Path:
    # In the main .app: Contents/MacOS/quickmd -> Contents/Helpers/QuickMDNotify.app
    return (
        Path(sys.executable).resolve().parent.parent
        / "Helpers"
        / "QuickMDNotify.app/Contents/MacOS/QuickMDNotify"
    )


def _windows(status: bool, title: str = "", body: str = "") -> str:
    import base64

    encoded = base64.b64encode(WINDOWS_SCRIPT.encode("utf-16le")).decode("ascii")
    environment = {
        **os.environ,
        "QUICKMD_NOTIFY_STATUS": "1" if status else "0",
        "QUICKMD_NOTIFY_TITLE": title,
        "QUICKMD_NOTIFY_BODY": body,
    }
    executable = Path(os.environ.get("SystemRoot", r"C:\Windows")) / (
        "System32/WindowsPowerShell/v1.0/powershell.exe"
    )
    result = subprocess.run(
        [str(executable), "-NoProfile", "-NonInteractive", "-EncodedCommand", encoded],
        env=environment,
        capture_output=True,
        text=True,
        timeout=20,
        check=True,
        creationflags=0x08000000,
    )
    return result.stdout.strip()


def notification_status() -> str:
    try:
        if sys.platform == "win32":
            return _windows(True) or "unknown"
        if sys.platform == "darwin" and _helper().is_file():
            result = subprocess.run(
                [str(_helper()), "--status"], capture_output=True, text=True, timeout=10, check=True
            )
            return result.stdout.strip() or "unknown"
    except (OSError, subprocess.SubprocessError):
        return "unavailable"
    return "unavailable (native notification helper not installed)"


def notify(results: list[Result]) -> None:
    if not results:
        return
    successes = [r for r in results if r.status == Status.SUCCESS]
    failed = sum(r.status == Status.FAILED for r in results)
    title = "일부 파일 변환 실패" if failed else "Markdown 변환 완료"
    body = f"성공 {len(successes)}개 / 실패 {failed}개"
    if len(successes) == 1 and not failed and successes[0].output:
        body = successes[0].output.name + " 파일이 생성되었습니다."
    try:
        if sys.platform == "win32":
            _windows(False, title, body)
        elif sys.platform == "darwin" and _helper().is_file():
            subprocess.run(
                [str(_helper()), title, body], capture_output=True, timeout=20, check=True
            )
    except (OSError, subprocess.SubprocessError):
        logging.warning("notification_failed")
