Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

Function Get-File($button)
{
    $OpenFileDialog = New-Object System.Windows.Forms.OpenFileDialog
    $OpenFileDialog.Title = "Please select file"
    $OpenFileDialog.InitialDirectory = Join-Path ($pwd).path "stanzas"
    $OpenFileDialog.filter = "Knock files (.fwknoprc) | *.fwknoprc"
    # Out-Null supresses the "OK" after selecting the file.
    $OpenFileDialog.ShowDialog() | Out-Null
    $button.Text = $OpenFileDialog.SafeFileName
    return $OpenFileDialog
}

Function KnockKnock($button)
{
    $StanzaObj = Get-File $button
    $WinStanzaPath = $StanzaObj.FileName
    $LinuxPath = (($WinStanzaPath -replace '\\','/') -replace ':','').ToLower().Trim('/')
    $WSLStanzaPath = "/mnt/$LinuxPath"
    $pinfo = New-Object System.Diagnostics.ProcessStartInfo
    $pinfo.FileName = "wsl.exe"
    $pinfo.RedirectStandardError = $true
    $pinfo.RedirectStandardOutput = $true
    $pinfo.UseShellExecute = $false
    $pinfo.Arguments = @("--distribution", "ubuntu", "fwknop", "--rc-file", $WSLStanzaPath, "--verbose")
    $p = New-Object System.Diagnostics.Process
    $p.StartInfo = $pinfo
    $p.Start() | Out-Null
    $stdout = $p.StandardOutput.ReadToEnd()
    $stderr = $p.StandardError.ReadToEnd()
    $p.WaitForExit()
    if ($p.ExitCode -ne 0)
    {
        Write-Host "Erorr occurred during Knock"
        Write-Host "stdout: $stdout"
        Write-Host "stderr: $stderr"
        Write-Host "exit code: " + $p.ExitCode
    }
    else
    {
        $StanzaSafeName = $StanzaObj.SafeFileName
        Write-Host "Successful knock with stanza: $StanzaSafeName"
    }
}

$form = New-Object System.Windows.Forms.Form
$form.Text = 'Knock Knock'
$form.Size = New-Object System.Drawing.Size(300,200)
$form.StartPosition = 'CenterScreen'

$closeButton = New-Object System.Windows.Forms.Button
$closeButton.Location = New-Object System.Drawing.Point(10,120)
$closeButton.Size = New-Object System.Drawing.Size(75,23)
$closeButton.Text = 'Cancel'
$closeButton.DialogResult = [System.Windows.Forms.DialogResult]::Cancel
$form.CancelButton = $closeButton
$form.Controls.Add($closeButton)

$label = New-Object System.Windows.Forms.Label
$label.Location = New-Object System.Drawing.Point(10,20)
$label.Size = New-Object System.Drawing.Size(260,20)
$label.Text = 'Please select your stanza'
$form.Controls.Add($label)

# Stanza selector
$stanzaButton = New-Object System.Windows.Forms.Button
$stanzaButton.Location = New-Object System.Drawing.Size(10,40)
$stanzaButton.Size = New-Object System.Drawing.Size(260,20)
$stanzaButton.Text = "Select Stanza"
$stanzaButton.add_click({KnockKnock $stanzaButton})
$form.AcceptButton = $stanzaButton
$form.Controls.Add($stanzaButton)

$form.Topmost = $true

$form.Add_Shown({$stanzaButton})
$form.ShowDialog()
