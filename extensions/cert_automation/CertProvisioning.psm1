function New-WdpRootCA {
    param ($CN = "WdpTestCA", $OutPath = "C:\temp\")

    $Subject = "CN=$CN"
    $RootCA = New-SelfSignedCertificate -CertStoreLocation cert:\CurrentUser\My -Subject $Subject -HashAlgorithm SHA512 -KeyUsage CertSign, CRLSign
    Export-Certificate -Cert $RootCA -FilePath "$OutPath$CN.cer"
    return $RootCA
}

function New-WdpDeviceCert {
    param (
        [string]$DnsName,
        [string]$OutPath = "C:\temp\",
        [string]$Password = "Wdp@1234",
        [string]$RootCAPath = "C:\temp\WdpTestCA.cer"
    )

    $Subject = "CN=$DnsName"
    $FileName = $DnsName -replace "[:\s]", "_" + ".pfx"
    $RootCA = Import-Certificate -FilePath $RootCAPath -CertStoreLocation Cert:\CurrentUser\My
    $DeviceCert = New-SelfSignedCertificate -DnsName $DnsName -CertStoreLocation cert:\LocalMachine\My -Subject $Subject -Signer $RootCA -HashAlgorithm SHA512
    Export-PfxCertificate -Cert $DeviceCert -FilePath "$OutPath$FileName" -Password (ConvertTo-SecureString -String $Password -Force -AsPlainText)
    return "$OutPath$FileName"
}

function Set-WdpCert {
    param (
        [string]$PfxPath,
        [string]$Password = "Wdp@1234"
    )

    Start-Process -FilePath WebManagement.exe -ArgumentList "-SetCert", $PfxPath, $Password -Verb RunAs -Wait
    Start-Sleep -Seconds 3
    sc stop webmanagement
    Start-Sleep -Seconds 2
    sc start webmanagement
}
