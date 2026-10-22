# Third-party notices

QuickMD uses [Microsoft MarkItDown](https://github.com/microsoft/markitdown), MIT license,
Copyright Microsoft Corporation. Conversion is performed by its public local-file API.
QuickMD is an independent project and is not affiliated with Microsoft.

Runtime components include Python (PSF), MarkItDown/Mammoth/openpyxl/python-pptx/pdfminer.six
(MIT), pandas/NumPy (BSD), lxml (BSD with libxml2/libxslt notices), Pillow (HPND),
cryptography (Apache-2.0/BSD), pdfplumber (MIT), pypdfium2/PDFium (Apache-2.0/BSD and
bundled third-party licenses), Magika (Apache-2.0), ONNX Runtime (MIT), psutil (BSD).
Magika's bundled model identifies file types; it is not OCR or image analysis.
ONNX telemetry is disabled before converter initialization. No model downloads occur.

PyInstaller is GPL-2.0-or-later with its bootloader distribution exception; that
exception permits distributing this application under its own license.
Inno Setup has its own permissive license; its compiler is a build tool, not a runtime dependency.

The build copies MarkItDown's recursive distribution metadata, including upstream
license files, into the frozen package. `scripts/licenses.py` exports a versioned
inventory and full installed runtime license texts into `dist/licenses/` for release
review. Preserve those notices when redistributing. Review transitive license changes
whenever updating either lock file; this summary does not replace their full texts.
