# Generates an encryption key
$EncryptionKeyBytes = New-Object Byte[] 32
[Security.Cryptography.RNGCryptoServiceProvider]::Create().GetBytes($EncryptionKeyBytes)
$OutDir = ($pwd).path
$EncryptionKeyBytes | Out-File "$OutDir/stanzakey.key"
