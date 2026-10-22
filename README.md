# QuickMD

**파일 우클릭으로 PDF·DOCX·PPTX·XLSX를 로컬 Markdown으로 변환합니다.**
Windows Explorer와 macOS Finder에 통합되며 설치된 버전은 Python·로그인·API Key가 필요 없습니다.
별도 GUI나 상주 서비스가 없습니다. [English guide](docs/README.en.md)

현재 **0.1.0 개발 버전**입니다. Windows x64와 macOS Apple Silicon 설치 파일을 CI에서 빌드·검증한 뒤 GitHub Actions 아티팩트로 제공합니다.
공개 GitHub Release·WinGet ID·Homebrew Tap은 아직 등록되지 않았습니다. [검증 기록과 미확인 항목](docs/VALIDATION.md)을 확인하세요.

## 주요 기능

- Microsoft MarkItDown 0.1.9를 사용해 네 가지 문서 형식을 변환합니다.
- 원본 옆에 UTF-8 Markdown을 저장하고, `report.md`가 있으면 `report (1).md`를 만듭니다.
- 원본·기존 출력을 보존하며 여러 프로세스의 저장 충돌도 원자적으로 처리합니다.
- 여러 파일을 순차 처리하고 실패가 있어도 계속합니다. 같은 배치의 중복 입력을 제거합니다.
- 우클릭 배치 요약 알림, CLI 결과, `doctor`·`repair`, 회전 로그를 제공합니다.

## 설치

지원 목표: Windows 10/11 x64, macOS 13+ Intel/Apple Silicon.

### 바로 다운로드 (Python 불필요)

현재 0.1.0 개발 빌드입니다. 링크를 눌러 ZIP을 받고 압축을 푸세요.

- [Windows x64 설치 프로그램 다운로드](https://github.com/whitewise95/quickmd-desktop/actions/runs/39797307725/artifacts/12432999826) — 압축을 푼 뒤 `QuickMD-Setup-Windows-x64.exe`를 실행합니다.
- [macOS Apple Silicon 설치 이미지 다운로드](https://github.com/whitewise95/quickmd-desktop/actions/runs/39797307725/artifacts/12434940174) — 압축을 푼 뒤 `QuickMD-macOS-arm64.dmg`를 열고 포함된 설치 안내를 따릅니다.

macOS Intel용 파일은 현재 준비 중입니다. GitHub Actions 아티팩트를 받으려면 GitHub 로그인이 필요합니다. 아티팩트는 90일 뒤 만료되므로 이 링크는 새 빌드를 만들 때 갱신합니다. 정식 GitHub Release는 아직 없습니다.

### 소스에서 직접 설치하기

아래 절차는 설치 파일을 직접 만들거나 macOS에 설치하려는 경우에 사용합니다. GitHub에서 소스를 clone하는 것만으로는 설치되지 않습니다.

#### 1. 소스 내려받기

먼저 Git과 QuickMD 빌드 도구를 설치합니다.

- **macOS:** 터미널에서 `xcode-select --install`을 실행해 Apple Command Line Tools를 설치하고 [Python 3.12](https://www.python.org/downloads/macos/)를 설치합니다. 이미 Homebrew가 있다면 `brew install python@3.12`를 사용할 수 있습니다.
- **Windows:** [Git](https://git-scm.com/download/win), [Python 3.12](https://www.python.org/downloads/windows/)(설치 시 Python Launcher `py` 포함), [Inno Setup 6](https://jrsoftware.org/isdl.php)을 설치합니다. Python과 Git 설치 프로그램은 기본 설치 옵션을 사용하면 됩니다.

그다음 원하는 위치에서 터미널(macOS) 또는 PowerShell(Windows)을 열어 저장소를 clone합니다. 예를 들어 홈 폴더의 Documents에 받으려면:

```bash
cd ~/Documents
git clone https://github.com/whitewise95/quickmd-desktop.git QuickMD
cd QuickMD
```

**중요:** 이후 명령은 모두 `QuickMD` 저장소 폴더 안에서 실행합니다. 다른 폴더에 있다면 먼저 `cd ~/Documents/QuickMD`를 실행하세요. `build/`와 `dist/`는 빌드할 때 생성되므로 clone 직후에는 아직 없습니다.

#### 2. 의존성 설치 및 빌드

현재 운영체제와 CPU에서 직접 빌드합니다. 전체 명령은 아래 개발·빌드 절에도 있습니다.

macOS:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install --require-hashes -r requirements-dev.lock
python -m pip install --no-deps --no-build-isolation -e .
python scripts/build.py
```

Windows PowerShell:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --require-hashes -r requirements-dev.lock
.\.venv\Scripts\python.exe -m pip install --no-deps --no-build-isolation -e .
.\.venv\Scripts\python.exe scripts\build.py
```

빌드가 끝나면 `dist` 폴더가 생깁니다. Windows 빌드는 Windows에서, macOS 빌드는 Mac에서 해야 합니다.

#### 3. 설치

macOS에서는 저장소 폴더에서 다음을 실행합니다.

```bash
bash build/dmg/install.sh
```

이 스크립트는 `build/dmg/QuickMD.app`을 사용자 계정에 설치합니다. 앱 위치는 `~/Library/Application Support/QuickMD/QuickMD.app`, CLI 명령 링크는 `~/.local/bin/quickmd`입니다. 새 터미널을 연 뒤 `quickmd doctor`로 확인하세요.

Windows에서는 파일 탐색기로 `dist\QuickMD-Setup-Windows-x64.exe`를 찾아 더블 클릭하고 설치 안내를 따릅니다. 관리자 권한 없이 `%LOCALAPPDATA%\Programs\QuickMD`에 설치되며 우클릭 메뉴도 등록합니다. 설치 후 새 PowerShell 창에서 `quickmd doctor`를 실행하세요.

**`Start-Process`에서 파일을 찾을 수 없다고 나오면:** 다운로드한 ZIP을 먼저 압축 해제하고, 그 폴더에서 `QuickMD-Setup-Windows-x64.exe`를 실행하세요. `dist\QuickMD-Setup-Windows-x64.exe` 경로는 저장소를 clone한 뒤 직접 빌드했을 때만 생깁니다. Git clone에는 `dist` 설치 파일이 들어 있지 않습니다. 직접 빌드한 경우 다음 명령으로 확인하세요.

```powershell
Test-Path .\dist\QuickMD-Setup-Windows-x64.exe
```

`True`이면 설치 파일이 생성된 것입니다. `False`이면 위 Windows 빌드 절차가 완료되지 않았거나 실패한 것입니다. 빌드 단계에 표시된 오류를 먼저 해결하세요. 설치된 QuickMD와 Actions에서 받은 사전 빌드 설치 파일은 Python 없이 사용할 수 있습니다. **소스에서 직접 빌드할 때만** Python 3.12와 Inno Setup 6이 필요합니다.

### 공개 배포 상태와 보안 알림

GitHub Releases에 정식 게시된 설치 파일, 공개 설치 스크립트, WinGet/Homebrew 설치 명령은 아직 없습니다. 이 개발 빌드는 공식 배포용 인증서로 서명·공증되지 않아 Windows SmartScreen 또는 macOS Gatekeeper 경고가 표시될 수 있습니다.

## 우클릭 사용

Windows: 파일 선택 → **Markdown으로 변환**. Windows 11에서는 **추가 옵션 표시** 안에 있을 수 있습니다.
클래식 레지스트리 메뉴를 사용하며 기본 메뉴용 COM 확장은 구현하지 않습니다.
Legacy `Player` 메뉴의 문서상 상한은 100개입니다. 초과 선택 또는 지원하지 않는 형식과 혼합 선택하면 메뉴가 숨겨질 수 있습니다.
지원 파일만 선택하거나 CLI를 사용하세요. 실제 Explorer에서 1/2/10/50/100개 선택 검증은 배포 전 필수입니다.

macOS: 파일 선택 → **빠른 동작** 또는 **서비스** → **Markdown으로 변환**.
`~/Library/Services/QuickMD — Markdown으로 변환.workflow`에 등록하며 모든 경로를 배열로 전달합니다.
메뉴가 없으면 시스템 설정의 서비스/확장 프로그램에서 활성화한 뒤 Finder를 다시 열어 확인하세요.
표시 위치는 OS 버전에 따라 다릅니다. 알림 권한·집중 모드 때문에 알림이 보이지 않아도 변환은 계속됩니다.

## CLI·진단

```bash
quickmd --version
quickmd --help
quickmd convert "사업계획서.pdf"
quickmd convert report.pdf manual.docx slides.pptx data.xlsx
quickmd convert -- -leading-hyphen.pdf
quickmd doctor
quickmd integrate
quickmd unintegrate
quickmd repair
quickmd uninstall
quickmd uninstall --purge-logs
```

종료 코드: **0** 성공/중복, **1** 하나 이상 실패 또는 운영 오류, **2** 사용법 오류.
`convert`는 파일별 결과와 합계를 터미널에 출력합니다.
내부 `shell-handler -- <파일들>`은 사용자별 큐로 요청을 모아 0.5초 단위로 처리합니다.
각 호출이 잠금을 기다리므로 종료 직전 요청도 다음 호출이 처리합니다.
다른 프로세스가 먼저 큐를 처리한 호출은 0을 반환합니다. 자동화에서 파일별 종료 코드가 필요하면 `convert`를 사용하세요.

`doctor`는 실행 경로·버전·OS·메뉴 등록 명령·알림 상태·실제 PDF 시험 변환을 검사합니다.
메뉴 등록 성공은 Finder/Explorer 화면 표시 확인과 다릅니다. `doctor --no-integration`은 설치 전 빌드 검사에 사용합니다.

## 업데이트·제거

실행 중인 변환을 마친 뒤 새 버전 설치 프로그램을 다시 실행합니다. 백그라운드 자동 업데이트는 없습니다.
macOS는 앱과 변경하는 설정 파일을 백업하고 실패 시 복원합니다. Windows는 고정 Inno AppId로 업데이트합니다.
손상된 설치는 재설치 후 `quickmd repair`로 복구하세요.

Windows: `quickmd uninstall` 또는 설정 → 설치된 앱 → QuickMD 제거.
macOS: `quickmd uninstall` 또는 다음 명령입니다.

```bash
bash "$HOME/Library/Application Support/QuickMD/uninstall.sh"
```

CLI는 공식 외부 제거 절차로 연결합니다. macOS에서는 호출한 CLI가 종료한 뒤 제거합니다.
앱·메뉴·CLI 연결·QuickMD가 추가한 PATH를 정리하며 변환된 Markdown은 보존합니다.
로그는 기본 보존하고 `--purge-logs`로 삭제합니다. 편집되거나 불완전한 PATH 블록은 사용자 설정 보호를 위해 남겨둡니다.

## 보안·알려진 제한

- 파일당 100 MiB, Office 압축 해제 합계 512 MiB/10,000항목, 변환 120초, 결과 32 MiB 제한입니다.
- 사용자별 전역 잠금으로 변환 프로세스 하나만 실행합니다. RSS를 50ms마다 감시해 2 GiB 초과 시 종료합니다. 순간적인 초과 할당을 막는 커널 메모리 샌드박스는 아닙니다.
- 로컬 파일을 비공개 임시 폴더에 복사해 `convert_local()`로 처리합니다. 네 개 변환기만 등록하고 플러그인을 비활성화합니다.
- 변환 프로세스의 Python 네트워크 연결·하위 프로세스 실행을 차단하고 ONNX 텔레메트리를 끕니다. 문서를 서버로 보내지 않으며 OCR·클라우드 SDK는 포함하지 않습니다. 악성 네이티브 코드에 대한 OS 샌드박스와는 다릅니다.
- 완성한 파일을 하드 링크로 공개하므로 APFS/NTFS 등 하드 링크 지원이 필요합니다. exFAT/FAT 또는 일부 네트워크·동기화 폴더에서는 실패할 수 있습니다. 로컬 폴더로 복사해 변환하세요.
- 정상 오류·시간 초과에는 임시 파일을 정리합니다. 강제 종료/전원 장애 시 `.quickmd-*.tmp` 또는 OS 임시 폴더의 `quickmd-*`가 남을 수 있습니다. 기존 출력은 보존됩니다.
- 로그는 시간·버전·형식·상태·오류 유형·소요 시간만 기록합니다. 본문·파일명·민감한 경로·원본 예외 메시지를 기록하지 않습니다. 1 MiB 파일과 백업 3개로 제한합니다.
- 로그 위치: Windows `%LOCALAPPDATA%\QuickMD\Data\logs`, macOS `~/Library/Application Support/QuickMD/logs`.
- PDF의 시각적 레이아웃을 완전히 재현하지 않습니다. 스캔 PDF에는 별도 OCR이 필요하며 빈 결과는 실패입니다. 암호화·손상 문서는 복구하거나 암호를 해제한 사본으로 변환하세요.
- 심볼릭 링크는 대상 내용을 읽고 선택한 링크 옆에 저장합니다. 실제 파일 ID로 중복을 판별합니다. 대소문자·Unicode 정규화 동등성은 파일시스템을 따릅니다.
- Windows 긴 경로 opt-in manifest를 포함하지만 OS 정책·라이브러리 제한이 있습니다. 읽기 전용 폴더, 디스크 부족, 오프라인 파일 등은 실패로 보고합니다.

## 개발·빌드

개발자에게만 Python 3.12가 필요합니다. macOS는 Xcode Command Line Tools, Windows는 Inno Setup 6가 필요합니다.
각 OS/CPU에서 직접 빌드합니다.

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install --require-hashes -r requirements-dev.lock
python -m pip install --no-deps --no-build-isolation -e .
python -m pytest -q
python -m ruff check src tests scripts
python -m mypy src/quickmd
python scripts/build.py
```

Windows: `py -3.12 -m venv .venv` 후 `.venv\Scripts\python.exe`로 위 `python` 명령을 실행하면 활성화가 필요 없습니다.
빌드 결과는 현재 플랫폼의 `dist/QuickMD-Setup-Windows-x64.exe` 또는
`dist/QuickMD-macOS-arm64.dmg` / `dist/QuickMD-macOS-x64.dmg`, `.sha256`, 라이선스 목록입니다.
태그를 푸시하면 CI가 세 플랫폼을 테스트·패키징하고 SHA256SUMS·빌드 증명이 포함된 개발용 초안 Release를 준비합니다. 일반 push 빌드에서 Windows 설치 프로그램은 Actions 아티팩트로 받을 수 있습니다.

```text
src/quickmd/        CLI, 변환, 안전 저장, 큐, 진단, OS 어댑터
tests/             실제 문서·경로·충돌·배치·프로세스·제거 테스트
packaging/         PyInstaller, Inno Setup, macOS Swift/설치 스크립트
scripts/           빌드, 다운로드 검증, 라이선스, 패키지 등록 준비
.github/workflows/ OS별 테스트·패키징·초안 Release
docs/              원본 요구사항, 설계, 배포·실기기 검증
```

Magika/ONNX는 MarkItDown의 파일 형식 식별에 필요한 의존성입니다. 이미지 분석/OCR 모델이 아닙니다.
NumPy 1.26.4·ONNX Runtime 1.20.1은 macOS 13용 바이너리를 고려해 고정했습니다.
`uv.lock`과 해시 포함 pip 잠금 파일을 함께 관리하며 업데이트 후 최소 OS 검증을 반복해야 합니다.

## 출처·라이선스

QuickMD: MIT. [Microsoft MarkItDown](https://github.com/microsoft/markitdown): MIT.
[재배포 라이선스](THIRD_PARTY_NOTICES.md), [공식 문서 조사](docs/RESEARCH.md), [배포 절차](docs/RELEASING.md)를 참고하세요.
