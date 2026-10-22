import argparse
import logging
import os
import subprocess
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

from quickmd import __version__
from quickmd.conversion import convert_batch
from quickmd.locking import file_lock
from quickmd.models import Result, Status
from quickmd.runtime import data_dir


def _logging() -> None:
    try:
        directory = data_dir() / "logs"
        directory.mkdir(parents=True, exist_ok=True, mode=0o700)
        handler = RotatingFileHandler(
            directory / "quickmd.log", maxBytes=1024 * 1024, backupCount=3, encoding="utf-8"
        )
        logging.basicConfig(
            level=logging.INFO,
            handlers=[handler],
            force=True,
            format="%(asctime)s %(levelname)s %(message)s",
        )
        logging.info("quickmd=%s platform=%s", __version__, sys.platform)
    except OSError:
        logging.basicConfig(handlers=[logging.NullHandler()], force=True)


def _print_results(results: list[Result]) -> None:
    for index, result in enumerate(results, 1):
        print(f"[{index}/{len(results)}] {result.source.name!r}")
        detail = repr(result.output.name) if result.output else result.message
        print(f"  {result.status.value.upper()} → {detail}")
    print(f"Completed: {sum(r.status == Status.SUCCESS for r in results)}")
    print(f"Failed: {sum(r.status == Status.FAILED for r in results)}")
    print(f"Skipped: {sum(r.status == Status.SKIPPED for r in results)}")


def _uninstall(purge_logs: bool) -> int:
    if not getattr(sys, "frozen", False):
        print("Source installation: run quickmd unintegrate, then python -m pip uninstall quickmd.")
        return 0
    executable = Path(sys.executable).resolve()
    if sys.platform == "win32":
        uninstaller = executable.parent / "unins000.exe"
        if not uninstaller.is_file():
            raise OSError("공식 제거 프로그램이 없습니다. 설치 프로그램으로 복구하세요.")
        arguments = [str(uninstaller)]
        if purge_logs:
            arguments.append("/PURGELOGS=1")
        subprocess.Popen(arguments, close_fds=True)
    elif sys.platform == "darwin":
        script = executable.parents[3] / "uninstall.sh"
        if not script.is_file():
            raise OSError("제거 스크립트가 없습니다. 공식 설치 프로그램으로 복구하세요.")
        argv = ["/bin/bash", str(script), "--wait-pid", str(os.getpid())]
        if purge_logs:
            argv.append("--purge-logs")
        subprocess.Popen(
            argv,
            start_new_session=True,
            close_fds=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    print("공식 제거 절차를 시작했습니다. 변환한 Markdown은 보존됩니다.")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="quickmd", description="로컬 Markdown 파일 변환")
    parser.add_argument("--version", action="version", version=f"QuickMD {__version__}")
    commands = parser.add_subparsers(dest="command", required=True)
    for name in ("convert", "shell-handler"):
        sub = commands.add_parser(name)
        sub.add_argument("paths", nargs="+")
    doctor_parser = commands.add_parser("doctor")
    doctor_parser.add_argument(
        "--no-integration",
        action="store_true",
        help="개발/빌드 검사 시 메뉴 미등록을 실패로 처리하지 않음",
    )
    for name in ("integrate", "unintegrate", "repair"):
        commands.add_parser(name)
    uninstall_parser = commands.add_parser("uninstall")
    uninstall_parser.add_argument("--purge-logs", action="store_true")
    args = parser.parse_args(argv)
    try:
        if args.command in ("convert", "shell-handler"):
            from quickmd.notifications import notify
            from quickmd.queue import drain, enqueue

            spool = data_dir() / "queue"
            shell = args.command == "shell-handler"
            if shell:
                enqueue(args.paths, spool)
            with file_lock(data_dir() / "conversion.lock"):
                _logging()
                results = drain(spool) if shell else convert_batch(args.paths)
                if shell:
                    notify(results)
                else:
                    _print_results(results)
            return 1 if any(r.status == Status.FAILED for r in results) else 0
        if args.command == "doctor":
            from quickmd.diagnostics import doctor

            with file_lock(data_dir() / "conversion.lock"):
                return doctor(require_integration=not args.no_integration)
        if args.command == "uninstall":
            return _uninstall(args.purge_logs)
        from quickmd.integration import integrate, integration_status, unintegrate

        if args.command == "unintegrate":
            unintegrate()
            print("QuickMD 메뉴를 제거했습니다.")
        else:
            integrate()
            if not integration_status():
                raise OSError("메뉴 등록 검증 실패")
            print("메뉴 등록 완료. Explorer/Finder에서 표시 여부를 확인하세요.")
        return 0
    except (OSError, ValueError, subprocess.SubprocessError):
        # Never expose arbitrary third-party exception text (paths/content).
        print(
            "QuickMD 작업 실패: 설치 경로, 권한, 저장 공간을 확인한 뒤 repair를 실행하세요.",
            file=sys.stderr,
        )
        return 1
