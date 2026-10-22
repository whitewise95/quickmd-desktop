$ErrorActionPreference = 'Stop'
if (-not $env:WINDOWS_CERT_PFX_BASE64) {
    Write-Output 'No signing secrets: building development artifacts.'
    exit 0
}
$file = Join-Path $env:RUNNER_TEMP 'quickmd-sign.pfx'
try {
    [IO.File]::WriteAllBytes($file, [Convert]::FromBase64String($env:WINDOWS_CERT_PFX_BASE64))
    $password = ConvertTo-SecureString $env:WINDOWS_CERT_PASSWORD -AsPlainText -Force
    $certificate = Import-PfxCertificate -FilePath $file -CertStoreLocation Cert:\CurrentUser\My -Password $password
    "WINDOWS_CERT_THUMBPRINT=$($certificate.Thumbprint)" >> $env:GITHUB_ENV
    $tool = Get-ChildItem 'C:\Program Files (x86)\Windows Kits\10\bin\*\x64\signtool.exe' | Sort-Object FullName | Select-Object -Last 1
    if (-not $tool) { throw 'signtool is missing' }
    "SIGNTOOL=$($tool.FullName)" >> $env:GITHUB_ENV
} finally {
    Remove-Item -LiteralPath $file -ErrorAction SilentlyContinue
}
