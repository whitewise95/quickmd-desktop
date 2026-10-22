param(
    [Parameter(Mandatory=$true)][ValidatePattern('^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$')][string]$Repository,
    [Parameter(Mandatory=$true)][ValidatePattern('^v[0-9]+\.[0-9]+\.[0-9]+$')][string]$Version,
    [Parameter(Mandatory=$true)][ValidatePattern('^[a-fA-F0-9]{64}$')][string]$Sha256
)
$ErrorActionPreference = 'Stop'
if (-not [Environment]::Is64BitOperatingSystem -or
    $env:PROCESSOR_ARCHITECTURE -eq 'ARM64' -or $env:PROCESSOR_ARCHITEW6432 -eq 'ARM64') {
    throw 'Windows x64 is required.'
}
if ([Environment]::OSVersion.Version.Major -lt 10) { throw 'Windows 10 or later is required.' }
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
$work = Join-Path ([IO.Path]::GetTempPath()) ('QuickMD-' + [Guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Path $work | Out-Null
try {
    $installer = Join-Path $work 'QuickMD-Setup-Windows-x64.exe'
    $url = "https://github.com/$Repository/releases/download/$Version/QuickMD-Setup-Windows-x64.exe"
    Invoke-WebRequest -UseBasicParsing -Uri $url -OutFile $installer
    if ((Get-FileHash -Algorithm SHA256 $installer).Hash -ne $Sha256) {
        throw 'SHA-256 mismatch; nothing installed.'
    }
    if ((Get-AuthenticodeSignature $installer).Status -ne 'Valid') {
        throw 'A valid publisher signature is required for public installation.'
    }
    $process = Start-Process -FilePath $installer -ArgumentList '/VERYSILENT','/SUPPRESSMSGBOXES','/NORESTART' -Wait -PassThru
    if ($process.ExitCode -ne 0) { throw "Installer failed: $($process.ExitCode)" }
    Write-Output 'QuickMD installed. Open a new terminal, then run quickmd doctor.'
} finally {
    Remove-Item -LiteralPath $work -Recurse -Force
}
