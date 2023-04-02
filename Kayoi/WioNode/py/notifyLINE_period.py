# 取得したデータを定期的にLINEに通知する

import datetime
import math
import requests
from Read_csv import Read_csv
from get_filepath import get_filepath
from recieve_username_auth import recieve_username_auth

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
    
    token_list= line_token_df[(line_token_df["通知目的"]== ("全般")) | (line_token_df["通知目的"]== ("定期"))]["アクセストークン"]

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

    #LINEに通知するメッセージを作る
    message  = '\n'
    #'センサ名:'+str(data番号)+'単位'+'\n'　センサ名、データ番号、単位を書く
    message += '■ハウス環境'+'\n'
    house_list = list(dict.fromkeys(data_latest_df["house_name"]))
    for house in house_list:
        df_house = data_latest_df[data_latest_df["house_name"] == house].copy()
        message += f"★{house}"+"\n"
        timestamp_checker = "I'm first-time and timestamp-changed flag"
        for _,row in data_latest_df.iterrows():
            timestamp = datetime.datetime.strptime(row["datetime"], "%Y-%m-%d %H:%M:%S").strftime("%m-%d %H:%M")
            if timestamp == timestamp_checker:
                pass
            else:
                message += f"{'日時':　>4}: {timestamp}"+"\n"
                timestamp_checker = timestamp    

            data = row["value"]
            datatype = row["datatype"]
            unit = datatype_setting_df.loc[datatype_setting_df["データの種類"] == datatype, "単位"].iloc[-1]
            if isinstance(unit, str):
                if unit.lower() == "nan":
                    unit = ""
            elif math.isnan(unit):
                    unit = ""

            message += f'{datatype:　>4}: {data:.2f}{unit}'+'\n'

    #LINEグループに通知を行う
    for token in token_list:
        payload = {'message' : message}
        headers = {'Authorization' : 'Bearer '+ token}
        r = requests.post(url99, data=payload, headers=headers)

    return

if recieve_username_auth():
    notify_LINE()