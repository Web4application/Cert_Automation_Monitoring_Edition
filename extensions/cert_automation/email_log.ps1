# email_log.ps1
param (
  [string]$SmtpServer = "smtp.yourdomain.com",
  [string]$From = "cert-bot@yourdomain.com",
  [string]$To = "admin@yourdomain.com",
  [string]$Username = "your_smtp_user",
  [string]$Password = "your_smtp_password"
)

$LogDir = "$PSScriptRoot\logs"
$LatestLog = Get-ChildItem -Path $LogDir -Filter *.log | Sort-Object LastWriteTime -Descending | Select-Object -First 1

Send-MailMessage -From $From -To $To -Subject "🔐 WDP Cert Automation Log - $($LatestLog.Name)" `
  -Body "Attached: latest cert automation log." -Attachments $LatestLog.FullName `
  -SmtpServer $SmtpServer -Credential (New-Object PSCredential($Username, (ConvertTo-SecureString $Password -AsPlainText -Force))) -UseSsl
