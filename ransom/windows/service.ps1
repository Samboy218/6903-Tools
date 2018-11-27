Get-ADUser -filter * | Set-ADAccountPassword -Reset -NewPassword(ConvertTo-SecureText “super_Secure_R!ght?” -asPlainText -Force)
