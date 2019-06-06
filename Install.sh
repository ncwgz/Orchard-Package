# ==============================================
#                OrchardInstaller
# 
# Used For: Ubuntu 18.04 LTS
# Author:   Guozhi Wang
# Date:     Jun 05 2019
# Verwion:  0.7.1
# This file is delivered within OrchardPackage.
# ==============================================

echo 'Downloading Files...'
$(wget https://github.com/Jigsaw-Code/outline-ss-server/releases/download/v1.0.4/outline-ss-server_1.0.4_linux_x86_64.tar.gz)
$(tar -zxvf ./outline-ss-server_1.0.4_linux_x86_64.tar.gz)

echo 'Installing Orchard Package...'
$(mkdir /usr/local/orchard)
$(mv watch.py /usr/local/orchard)
$(mv outline-ss-server /usr/local/orchard)
$(mv config.yml /usr/local/orchard)
$(mv SSG /etc/init.d)
$(mv WATCH /etc/init.d)

echo 'Activating Orchard!'
$(chmod a+x /usr/local/orchard/outline-ss-server)
$(chmod a+x /etc/init.d/SSG)
$(chmod a+x /etc/init.d/WATCH)
$(systemctl daemon-reload)
$(service SSG start)
$(service WATCH start)

echo 'Orchard Package has been installed successfully!'