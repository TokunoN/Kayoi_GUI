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

python3 ~/Desktop/Kayoi_GUI/Kayoi/WioNode/py/notifyLINE_alert.py
exit 0
