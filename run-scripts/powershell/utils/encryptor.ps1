# Encrypts your Stanza files.
param ([string]$FileName, [string]$StanzaFile)

$CurrentDIR = ($pwd).path
$ParentDIR = Split-Path $CurrentDIR -Parent
$EncryptionKeyData = Get-Content "$CurrentDIR/stanzakey.key"

$SecureStanzaData = Get-Content $StanzaFile -Raw | ConvertTo-SecureString -AsPlainText -Force
ConvertFrom-SecureString $SecureStanzaData -Key $EncryptionKeyData | Out-File -FilePath "$ParentDIR/stanzas/$FileName.fwknoprc"
