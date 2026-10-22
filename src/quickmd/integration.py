import platform
import sys

from quickmd.runtime import shell_command


def supported_os() -> bool:
    if sys.platform == "win32":
        return sys.getwindowsversion().major >= 10 and platform.machine().lower() in (
            "amd64",
            "x86_64",
        )
    if sys.platform == "darwin":
        return int(platform.mac_ver()[0].split(".")[0]) >= 13
    return False


def integrate() -> None:
    if not supported_os():
        raise OSError("지원 OS: Windows 10/11 x64, macOS 13 이상")
    if sys.platform == "win32":
        from quickmd.platforms.windows import integrate as install

        install(shell_command())
    else:
        from quickmd.platforms.macos import install_workflow, refresh_services

        install_workflow(shell_command())
        refresh_services()


def unintegrate() -> None:
    if sys.platform == "win32":
        from quickmd.platforms.windows import unintegrate as remove

        remove()
    elif sys.platform == "darwin":
        from quickmd.platforms.macos import refresh_services, remove_workflow

        remove_workflow()
        refresh_services()


def integration_status() -> bool:
    if sys.platform == "win32":
        from quickmd.platforms.windows import integration_status as check

        return check(shell_command())
    if sys.platform == "darwin":
        from quickmd.platforms.macos import workflow_status

        return workflow_status(shell_command())
    return False
