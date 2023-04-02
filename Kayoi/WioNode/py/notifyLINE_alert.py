# 取得したデータを定期的にLINEに通知する
# Ambientからデータを取得してから警報を送るのではなく、
# センサでデータを取得した段階での値で警報を通知する。
# 警報はできるだけ早く確実に知らせることが重要と思われるため、
# 複数回通信することを嫌った形。

import requests
from Read_csv import Read_csv
import os
import datetime
import math

from get_filepath import get_filepath

# LINEに通知を送る
def notify_LINE():

    file = "../resource/WioNode_data_latest.csv"
    filepath = get_filepath(file)
    try:
        with Read_csv(filepath) as df:
            data_latest_df = df
    except FileNotFoundError:
        message = "WioNodeから得たデータを記録したファイルが存在しません"
        file = "../stderr.log"
        filepath = get_filepath(file)
        with open(filepath, mode = "a") as f:
            f.write(message + "\n")
        return

    file = "../resource/line_token.csv"
    try:
        with Read_csv(get_filepath(file)) as df:
            line_token_df = df
    except FileNotFoundError:
        message = "LINE Notifyのトークンをまとめたファイルが存在しません"
        file = "../stderr.log"
        filepath = get_filepath(file)
        with open(filepath, mode = "a") as f:
            f.write(message + "\n")
        return
    token_alert_list= line_token_df[(line_token_df["通知目的"]== ("全般")) | (line_token_df["通知目的"]== ("警報"))]["アクセストークン"]

    file = "../resource/datatype_setting.csv"
    filepath = get_filepath(file)
    try:
        with Read_csv(filepath) as df:
            datatype_setting_df = df
    except FileNotFoundError:
        message = "データの種類に関する情報をまとめたファイルが存在しません"
        file = "../stderr.log"
        filepath = get_filepath(file)
        with open(filepath, mode = "a") as f:
            f.write(message + "\n")
        return

    #LINE notify のURL
    url99 = "https://notify-api.line.me/api/notify"

    # 警報を通知する
    alert_message = "\n"
    timestamp_checker = "I'm first-time and timestamp-changed flag"
    for _,row in data_latest_df.iterrows():
        timestamp = datetime.datetime.strptime(row["datetime"], "%Y-%m-%d %H:%M:%S").strftime("%m-%d %H:%M")
        if timestamp == timestamp_checker:
            pass
        else:
            alert_message += f"日時: {timestamp}"+"\n"
            timestamp_checker = timestamp    
        alert_message += "\n"

        data = row["value"]
        datatype_ser = datatype_setting_df.loc[datatype_setting_df["データの種類"] == row["datatype"], :]
        if data <= datatype_ser["下限閾値"].iloc[-1]:
            alert = datatype_ser["下限警告文"].iloc[-1]
        elif data >= datatype_ser["上限閾値"].iloc[-1]:
            alert = datatype_ser["上限警告文"].iloc[-1]
        else:
            continue

        house = row["house_name"]
        unit = datatype_ser["単位"].iloc[-1]
        if isinstance(unit, str):
            if unit.lower() == "nan":
                unit = ""
        elif math.isnan(unit):
                unit = ""

        alert_message += f"{alert}！　{house}: {data:.2f}{unit}"+"\n"
        
    if alert_message == "\n":
        print("no alert")
        return

    for token_alert in token_alert_list:
        # 実行フラグによる判断を入れるならここ。
        payload = {'message' : alert_message}
        headers = {'Authorization' : 'Bearer '+ token_alert}
        r = requests.post(url99, data=payload, headers=headers)

    return

notify_LINE()