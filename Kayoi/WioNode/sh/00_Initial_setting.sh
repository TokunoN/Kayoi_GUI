#!/bin/bash

echo インストール状況 -> stdout.log
echo エラーの確認     -> stderr.log

sudo chmod 774 -R ../../../
python3 ../py/set_sh_LF.py

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

# dash -> bash
# cronなどからshを実行できるようにする
# リダイレクトが使えるようになる。
echo "dash dash/sh boolean false" | sudo debconf-set-selections
sudo dpkg-reconfigure --frontend=noninteractive dash



sudo apt-get update
sudo apt-get upgrade
sudo apt-get -y install i2c-tools 
sudo apt-get -y install python3-pandas
sudo apt-get -y install python3-matplotlib
sudo apt-get -y install python3-seaborn
sudo apt-get -y install python3-requests
sudo apt-get -y install python3-numpy
sudo apt-get -y install python3-tk
sudo apt-get -y install python3-openpyxl
sudo pip -y install python-crontab
sudo pip -y install smbus
sudo pip -y install git+https://github.com/AmbientDataInc/ambient-python-lib.git
sudo pip -y install flet==0.3.2

cd ~/Desktop
wget -O NotoSansJP.zip https://noto-website-2.storage.googleapis.com/pkgs/NotoSansJP.zip
unzip -d NotoSansJP NotoSansJP.zip
sudo cp -afv NotoSansJP/NotoSansJP-Light.otf ../py/assets/fonts
sudo mkdir -p /usr/share/fonts/opentype
sudo mv -fv NotoSansJP /usr/share/fonts/opentype/noto
rm -rfv NotoSansJP.zip
sudo fc-cache -fv

sudo apt install ibus-mozc

sudo reboot


exit 0
