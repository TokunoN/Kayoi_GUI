#!/bin/bash

LOG_OUT="$HOME/Desktop/Kayoi_GUI/Kayoi/WioNode/stdout.log"
LOG_ERR="$HOME/Desktop/Kayoi_GUI/Kayoi/WioNode/stderr.log"
touch "$LOG_OUT"
touch "$LOG_ERR"
sudo chmod 774 "$LOG_OUT"
sudo chmod 774 "$LOG_ERR"


exec 1>>"$LOG_OUT"
exec 2> >(
  while read -r l; do echo "[$(date +"%Y-%m-%d %H:%M:%S")] $l"; done \
    | tee -a "$LOG_ERR"
)

cd /etc/systemd
sudo cp -p timesyncd.conf timesyncd.conf.org
sudo nano /etc/systemd/timesyncd.conf

#NTP=ntp.jst.mfeed.ad.jp ntp.nict.jp
#FallbackNTP=time.google.com

sudo timedatectl set-ntp true

sudo systemctl daemon-reload
sudo systemctl restart systemd-timesyncd.service

ps -ax | grep "time"

sudo systemctl status systemd-timesyncd

exit 0
