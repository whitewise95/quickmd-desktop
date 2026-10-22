import os
import plistlib
import shlex
import shutil
import subprocess
import tempfile
from pathlib import Path

WORKFLOW = "QuickMD — Markdown으로 변환.workflow"
BUNDLE_ID = "org.quickmd.convert"


def services_dir() -> Path:
    return Path.home() / "Library" / "Services"


def workflow_document(launcher: list[str]) -> dict[str, object]:
    script = "exec " + shlex.join([*launcher, "shell-handler", "--"]) + ' "$@"'
    action = {
        "AMAccepts": {"Container": "List", "Optional": True, "Types": ["com.apple.cocoa.string"]},
        "AMActionVersion": "2.0.3",
        "AMApplication": ["Automator"],
        "AMParameterProperties": {"COMMAND_STRING": {}, "inputMethod": {}, "shell": {}},
        "AMProvides": {"Container": "List", "Types": ["com.apple.cocoa.string"]},
        "ActionBundlePath": "/System/Library/Automator/Run Shell Script.action",
        "ActionName": "Run Shell Script",
        "ActionParameters": {
            "COMMAND_STRING": script,
            "inputMethod": 1,
            "shell": "/bin/bash",
            "source": "",
            "CheckedForUserDefaultShell": True,
        },
        "BundleIdentifier": "com.apple.RunShellScript",
        "CFBundleVersion": "2.0.3",
        "CanShowSelectedItemsWhenRun": False,
        "CanShowWhenRun": False,
        "Category": ["AMCategoryUtilities"],
        "Class Name": "RunShellScriptAction",
        "InputUUID": "35D0F472-F141-454B-A72F-D0B66CF8DB2B",
        "OutputUUID": "D28A6790-79DD-45AA-9B5E-87BEEA0EE615",
        "UUID": BUNDLE_ID,
        "isViewVisible": 1,
    }
    return {
        "AMApplicationBuild": "523",
        "AMApplicationVersion": "2.10",
        "AMDocumentVersion": "2",
        "actions": [{"action": action}],
        "connectors": [],
        "workflowMetaData": {
            "workflowTypeIdentifier": "com.apple.Automator.servicesMenu",
            "serviceInputTypeIdentifier": "com.apple.Automator.fileSystemObject",
            "serviceOutputTypeIdentifier": "com.apple.Automator.nothing",
            "serviceProcessesInput": 0,
            "serviceApplicationBundleID": "com.apple.finder",
            "serviceApplicationPath": "/System/Library/CoreServices/Finder.app",
            "useAutomaticInputType": False,
        },
    }


def install_workflow(launcher: list[str], services: Path | None = None) -> Path:
    services = services or services_dir()
    services.mkdir(parents=True, exist_ok=True)
    destination = services / WORKFLOW
    if destination.exists():
        _check_owned(destination)
    temporary = Path(tempfile.mkdtemp(prefix=".quickmd-workflow-", dir=services))
    try:
        contents = temporary / "Contents"
        contents.mkdir()
        info = {
            "CFBundleIdentifier": BUNDLE_ID,
            "CFBundleName": "Markdown으로 변환",
            "NSServices": [
                {
                    "NSMenuItem": {"default": "Markdown으로 변환"},
                    "NSMessage": "runWorkflowAsService",
                    "NSSendFileTypes": [
                        "com.adobe.pdf",
                        "org.openxmlformats.wordprocessingml.document",
                        "org.openxmlformats.presentationml.presentation",
                        "org.openxmlformats.spreadsheetml.sheet",
                    ],
                    "NSRequiredContext": {"NSApplicationIdentifier": "com.apple.finder"},
                }
            ],
        }
        (contents / "Info.plist").write_bytes(plistlib.dumps(info))
        (contents / "document.wflow").write_bytes(plistlib.dumps(workflow_document(launcher)))
        if destination.exists():
            # Replace only our two files, preserving any unrelated bundle contents.
            for name in ("Info.plist", "document.wflow"):
                os.replace(contents / name, destination / "Contents" / name)
        else:
            temporary.rename(destination)
    finally:
        if temporary.exists():
            shutil.rmtree(temporary)
    return destination


def _check_owned(path: Path) -> None:
    if path.is_symlink() or (path / "Contents").is_symlink():
        raise OSError("Refusing to change a symlinked workflow")
    info = plistlib.loads((path / "Contents/Info.plist").read_bytes())
    if info.get("CFBundleIdentifier") != BUNDLE_ID:
        raise OSError("Workflow name belongs to another application")


def remove_workflow(services: Path | None = None) -> None:
    destination = (services or services_dir()) / WORKFLOW
    if destination.exists():
        _check_owned(destination)
        shutil.rmtree(destination)


def workflow_status(launcher: list[str], services: Path | None = None) -> bool:
    path = (services or services_dir()) / WORKFLOW
    try:
        _check_owned(path)
        actual = plistlib.loads((path / "Contents/document.wflow").read_bytes())
        return bool(actual == workflow_document(launcher))
    except (OSError, ValueError, plistlib.InvalidFileException):
        return False


def refresh_services() -> None:
    subprocess.run(
        ["/System/Library/CoreServices/pbs", "-update"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        timeout=20,
        check=False,
    )
