# センサからデータを取得する
# 取得したデータをAmbientに送信する

import ambient
import pandas as pd
import datetime
import os
from AmbientDataHandler import AmbientDataHandler
from SHT31 import SHT31
from get_filepath import get_filepath

adh = AmbientDataHandler()
write_config_df = adh.fetch_ambient_write_config()
data_df = pd.DataFrame(columns=["datetime","house_name","sensor_name","chID","dataID","writeKey", "datatype","data"])
now = datetime.datetime.now()
nowstr = now.strftime("%Y-%m-%d %H:%M:%S.%f")

# SHT31 によってデータを取得する。
sht31_config_df = write_config_df[write_config_df["sensor_name"] == "SHT31"].reset_index(drop = True)
sht31 = SHT31()
# 1つのラズパイに複数のSHT31を接続している場合は、
# sht31_i2c_addr_list に適切なアドレスを追加し、forループを回す。
sht31_i2c_addr_list = [0x45]
for i in range(len(sht31_config_df) // 2):
    sht31.i2c_addr = sht31_i2c_addr_list[i]
    temperature, humidity = sht31.get_temperature_and_humidity()

    treat_df = sht31_config_df.loc[i*2:i*2+1, :].copy()
    treat_df.loc[:,["datetime", "data"]] = None
    # setting with copy warning: たぶん対応できた。
    treat_df.loc[treat_df["datatype"] == "気温", "data"] = temperature
    treat_df.loc[treat_df["datatype"] == "湿度", "data"] = humidity
    data_df = pd.concat([data_df, treat_df], axis=0)

# I2C機器を追加するならば、その機器に対応した記述を適宜追加する。

# 日付をdata_dfに設定する。
data_df.loc[:,"datetime"] = nowstr

# データをcsvに保存
# Ambientに送信できない時の保険
file = "../resource/I2C_data_local.csv"
filepath = get_filepath(file)
save_df = data_df.drop("writeKey", axis=1)
save_df.to_csv(filepath, mode='a', header= not os.path.exists(filepath), index=False, encoding="shift-jis")

# 定期通知や警報通知に用いるためのcsv書き出し
file = "../resource/I2C_data_latest_local.csv"
filepath = get_filepath(file)
save_df.to_csv(filepath, mode='w', header=True, index=False, encoding="shift-jis")

# データをAmbientに送信する
for chID in set(data_df["chID"]):
    treat_df = data_df.loc[data_df["chID"] == chID, :]
    send_dict = {"crated": nowstr}
    for dataID in set(treat_df["dataID"]):
        send_dict[f"{dataID}"] = treat_df.loc[treat_df["dataID"] == dataID, "data"].iloc[-1]
    writeKey = treat_df.loc[treat_df["chID"] == chID, "writeKey"].iloc[-1]
    am = ambient.Ambient(chID, writeKey)
    r = am.send(send_dict)