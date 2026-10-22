import platform
import sys
import tempfile
from pathlib import Path

from quickmd import __version__
from quickmd.conversion import convert_batch
from quickmd.integration import integration_status, supported_os
from quickmd.models import Status
from quickmd.notifications import notification_status


def sample_pdf() -> bytes:
    text = b"BT /F1 12 Tf 72 720 Td (QuickMD self test) Tj ET"
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
        b"/Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
        b"<< /Length " + str(len(text)).encode() + b" >>\nstream\n" + text + b"\nendstream",
    ]
    data = b"%PDF-1.4\n"
    offsets = []
    for number, obj in enumerate(objects, 1):
        offsets.append(len(data))
        data += f"{number} 0 obj\n".encode() + obj + b"\nendobj\n"
    xref = len(data)
    data += b"xref\n0 6\n0000000000 65535 f \n"
    data += b"".join(f"{offset:010} 00000 n \n".encode() for offset in offsets)
    return data + f"trailer\n<< /Size 6 /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF\n".encode()


def doctor(*, require_integration: bool = True) -> int:
    print(f"QuickMD Diagnostics {__version__}")
    print(f"OS: {platform.system()} {platform.release()} ({platform.machine()})")
    print(f"Executable: {sys.executable}")
    os_ok = supported_os()
    print(f"Supported OS: {'OK' if os_ok else 'FAILED'}")
    menu_ok = integration_status()
    print(f"Context Menu / Quick Action: {'REGISTERED' if menu_ok else 'MISSING / STALE'}")
    print("Menu visibility: MANUAL CHECK (Explorer/Finder)")
    print(f"Notification: {notification_status()}")
    with tempfile.TemporaryDirectory(prefix="quickmd-doctor-") as directory:
        path = Path(directory) / "self-test.pdf"
        path.write_bytes(sample_pdf())
        result = convert_batch([str(path)])[0]
        engine_ok = (
            result.status == Status.SUCCESS
            and result.output is not None
            and "QuickMD self test" in result.output.read_text(encoding="utf-8")
        )
        print(f"MarkItDown / test conversion: {'OK' if engine_ok else 'FAILED'}")
    if not menu_ok:
        print("Suggested action: quickmd repair; then check OS Services/Extensions settings.")
    print("Notification disabled/unavailable: check OS notification settings for QuickMD.")
    return 0 if os_ok and engine_ok and (menu_ok or not require_integration) else 1
