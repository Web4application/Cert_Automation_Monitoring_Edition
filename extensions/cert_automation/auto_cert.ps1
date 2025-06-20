$CNs = @("localhost", "127.0.0.1", "devbox.local")
$OutputPath = "C:\WdpCertAutomation\certs\"
$LogFile = "C:\WdpCertAutomation\logs\cert_log.txt"
$CertPassword = ConvertTo-SecureString -String "Wdp@1234" -Force -AsPlainText

# Logging setup
Start-Transcript -Path $LogFile -Append

# Root CA lookup
$RootCA = Get-ChildItem -Path Cert:\CurrentUser\My | Where-Object { $_.Subject -like "*PickAName*" }

# Generate device cert
$DeviceCert = New-SelfSignedCertificate `
  -DnsName $CNs `
  -CertStoreLocation "cert:\CurrentUser\My" `
  -Signer $RootCA `
  -KeyAlgorithm RSA `
  -KeyLength 2048 `
  -HashAlgorithm SHA256 `
  -KeyExportPolicy Exportable `
  -TextExtension @("2.5.29.19={critical}{text}") `
  -NotAfter (Get-Date).AddDays(90)

# Export files
$pfxPath = Join-Path $OutputPath "DeviceCert.pfx"
$cerPath = Join-Path $OutputPath "DeviceCert.cer"
Export-PfxCertificate -Cert $DeviceCert -FilePath $pfxPath -Password $CertPassword
Export-Certificate -Cert $DeviceCert -FilePath $cerPath

# Rebind
$Thumbprint = $DeviceCert.Thumbprint
netsh http delete sslcert ipport=0.0.0.0:44300
netsh http add sslcert ipport=0.0.0.0:44300 certhash=$Thumbprint appid="{00112233-4455-6677-8899-AABBCCDDEEFF}"

# Optional: Notify or log cert expiry date
$expiry = $DeviceCert.NotAfter
Write-Output "Certificate expires on: $expiry"

Stop-Transcript

# Log structured event
$eventLogPath = "$ScriptDir\cert_events.json"

$logData = @{
    timestamp = (Get-Date).ToString("o")
    issued_dns = $targets
    root_ca = $root.Subject
    cert_files = Get-ChildItem -Path $OutPath -Filter *.pfx | Select-Object -ExpandProperty Name
    status = "success"
}

if (Test-Path $eventLogPath) {
    $existing = Get-Content $eventLogPath | ConvertFrom-Json
    $all = $existing + $logData
} else {
    $all = @($logData)
}

$all | ConvertTo-Json -Depth 5 | Set-Content $eventLogPath -Encoding UTF8
