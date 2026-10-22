# Native build only: python -m PyInstaller --clean --noconfirm packaging/quickmd.spec
import os
import sys
from pathlib import Path
from PyInstaller.utils.hooks import collect_data_files, copy_metadata

root = Path(SPECPATH).parent
datas = collect_data_files("magika")
datas += copy_metadata("markitdown", recursive=True)
datas += [(str(root / "LICENSE"), "licenses"), (str(root / "THIRD_PARTY_NOTICES.md"), "licenses")]
datas += [(str(root / "build/licenses"), "licenses/runtime")]
analysis = Analysis(
    [str(root / "packaging/launcher.py")], pathex=[str(root / "src")],
    binaries=[], datas=datas,
    hiddenimports=["quickmd.__main__", "markitdown.converters", "pdfminer", "pdfplumber",
                   "mammoth", "openpyxl", "pptx", "pandas", "onnxruntime", "psutil"],
    excludes=["pytest", "mypy", "ruff", "reportlab", "pypdf", "tkinter", "matplotlib",
              "scipy", "IPython", "azure", "openai", "boto3", "torch", "tensorflow"],
    noarchive=False,
)
pyz = PYZ(analysis.pure)
settings = dict(exclude_binaries=True, debug=False, strip=False, upx=False,
                manifest=str(root / "packaging/windows/quickmd.manifest")
                if sys.platform == "win32" else None,
                codesign_identity=os.environ.get("APPLE_SIGN_IDENTITY") or None,
                entitlements_file=str(root / "packaging/macos/entitlements.plist")
                if sys.platform == "darwin" else None)
cli = EXE(pyz, analysis.scripts, [], name="quickmd", console=True, **settings)
executables = [cli]
if sys.platform == "win32":
    shell = EXE(pyz, analysis.scripts, [], name="quickmd-shell", console=False, **settings)
    executables.append(shell)
collection = COLLECT(*executables, analysis.binaries, analysis.datas, strip=False,
                     upx=False, name="QuickMD")
if sys.platform == "darwin":
    app = BUNDLE(collection, name="QuickMD.app", bundle_identifier="org.quickmd.desktop",
                 info_plist={"CFBundleShortVersionString": "0.1.0", "CFBundleVersion": "1",
                             "LSMinimumSystemVersion": "13.0", "LSUIElement": True,
                             "NSHighResolutionCapable": True})
