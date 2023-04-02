# WioNodeを通じてセンサからデータを取得する
# 定期的に実行することを想定

import numpy as np
import pandas as pd
import datetime
import time
import os
import requests
from decimal import Decimal, ROUND_HALF_UP #四捨五入に用いる

from get_filepath import get_filepath
from Read_csv import Read_csv


class WioNodeDataGetting():
    def wndg(self):
        file = "../resource/WioNode_setting.csv"
        try:
            with Read_csv(get_filepath(file)) as df:
                WioNode_setting_df = df
        except FileNotFoundError:
            message = "WioNodeのトークンをまとめたファイルが存在しません"
            file = "../stderr.log"
            filepath = get_filepath(file)
            with open(filepath, mode = "a") as f:
                f.write(message + "\n")
            return

        df = pd.DataFrame(index = WioNode_setting_df.index)
        df["datetime"] = datetime.datetime.now().replace(microsecond=0)
        df[["house_name", "datatype", "value"]] = pd.DataFrame(WioNode_setting_df.apply(self.apply_WioNode_data_getting, axis = 1).to_list(), index = WioNode_setting_df.index)
        
        return df
        
    def apply_WioNode_data_getting(self, row):
        
        self.CONNECTION_RETRY = 3 #データ取得を行う最大試行数を設定する
        self.INTERVAL_TIME = 5 #データ取得失敗時に何秒待つかを設定する
        
        # self.value を求める
        self.token = row["アクセストークン"]
        self.WioNode_data_getting(self.token)
        
        self.house_name = row["ハウス名"]
        self.datatype = row["データの種類"]
        return [self.house_name, self.datatype, self.value]
        
    def WioNode_data_getting(self, token):
        if self.CONNECTION_RETRY < 0:
            return 
        try:
            data_json = requests.get(token).json()
        
        except requests.exceptions.MissingSchema:
            # ダミーデータ生成用
            if isinstance(token, str) == False:
                token = "temperture"
            data_json = {f"{token}": np.random.randint(0,100) }
        
        for key in data_json:
            if "error" in data_json:
                self.error_handling(data_json[key])
                return
            self.value = float(Decimal(str(data_json[key])).quantize(Decimal('0.1'), rounding=ROUND_HALF_UP))
            return
            
    def error_handling(self, value):
        if value == "Node is offline":
            self.value = ' OFF'#マイコンに電源が来ていないかWiFiの電源がオフです
            return

        elif value == "timeout":
            self.value = 'TIME'#マイコン再起動中かWiFiの調子が悪いです
            time.sleep(self.INTERVAL_TIME)
            self.CONNECTION_RETRY -= 1
            self.WioNode_data_getting(self.token)
                        
        elif value == "METHOD":
            self.value = 'FWUP'#Wioアプリでのファームウェアアップデート失敗か、アプリで接続しているセンサが正しいかを確認してください
            return

        elif value == "Unknown":
            self.value = ' UNK'#センサが壊れているか、センサが抜けています。
            time.sleep(self.INTERVAL_TIME)
            self.CONNECTION_RETRY -= 1
            self.WioNode_data_getting(self.token)
            
        else:
            self.value = 'FAIL'#データ取得に失敗しました。WiFiの電波が弱いか、マイコンの調子が悪いかもしれません。
            time.sleep(self.INTERVAL_TIME)
            self.CONNECTION_RETRY -= 1
            self.WioNode_data_getting(self.token)
            

def error_to_nan(row):
    # エラー内容を記録するとグラフにするときに厄介と思われるのでnanに変換する
    value = row["value"]
    if isinstance(value, float) == False:
        error_message_dict = {
            ' OFF': "マイコンに電源が来ていないかWiFiの電源がオフです。",
            'TIME': "マイコン再起動中かWiFiの調子が悪いです。",
            'FWUP': "Wioアプリでのファームウェアアップデート失敗か、アプリで接続しているセンサが正しいかを確認してください。", 
            ' UNK': "センサが壊れているか、センサが抜けています。", 
            'FAIL': "データ取得に失敗しました。WiFiの電波が弱いか、マイコンの調子が悪いかもしれません。"
        }
        message = f"{row['datetime'].strftime('%Y-%m-%d %H:%M:%S')}, "
        message += f"{row['house_name']}, "
        message += f"{row['datatype']}, "
        message += f"{value}, "
        message += f"{error_message_dict[value]}"
        message += "\n"
        
        file = "../stderr.log"
        filepath = get_filepath(file)
        with open(filepath, mode = "a") as f:
            f.write(message)
        row["value"] = float("nan")
    return row

df = WioNodeDataGetting().wndg()

df = df.apply(error_to_nan, axis=1)

file = "../resource/WioNode_data_latest.csv"
filepath = get_filepath(file)
df.to_csv(filepath, mode="w", encoding="shift-jis", header = True, index=False)

file = "../resource/WioNode_data_period.csv"
filepath = get_filepath(file)
df.to_csv(filepath, mode="a", encoding="shift-jis", header = not os.path.exists(filepath), index=False)