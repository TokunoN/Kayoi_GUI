# Ambient関連の設定を読み込み、Ambientへ送受信するための設定を整理して返す

import getpass
import openpyxl
import pandas as pd
from get_filepath import get_filepath



class AmbientDataHandler():
    def __init__(self) -> None:
        # 設定ファイルを読み込む
        file = "../resource/AmbientSetting.xlsx"
        filepath = get_filepath(file)
        try:
            self.wb = openpyxl.load_workbook(filepath)
        except FileNotFoundError:
            message = "Ambientの設定をまとめたファイルが存在しません"
            file = "../stderr.log"
            filepath = get_filepath(file)
            with open(filepath, mode = "a") as f:
                f.write(message + "\n")
            return
        self.chInfo_df = self.convert_excelsheet_into_df(self.wb["chInfo"])

        self.username = getpass.getuser()
        # self.date_query = None

    def convert_excelsheet_into_df(self, sheet):
        # エクセルシートの入力内容を2次元リスト経由でDataFrameに変換する
        g_all = sheet.values
        l_2d = [[cell for cell in row] for row in g_all]
        df = pd.DataFrame(l_2d, columns = l_2d[0]).drop([0], axis = 0)
        return df

    def fetch_ambient_write_config(self):
        # Ambientに書き込むための設定を読み込む
        return_df = pd.DataFrame(columns=["house_name", "sensor_name", "chID", "dataID", "writeKey", "datatype"])

        for i in self.chInfo_df.index:
            ch_num = self.chInfo_df.loc[i, "chNumber"] 
            ch_ID = self.chInfo_df.loc[i, "chID"]
            write_key = self.chInfo_df.loc[i, "writeKey"]
            if (ch_ID == None) or (write_key == None):
                continue
            else:
                ch_df = self.convert_excelsheet_into_df(self.wb[f"{ch_num}"])
                # ラズパイのユーザー名に依存して送信するデータのIDを指定する。
                ch_df = ch_df[ch_df["raspi_name"] == self.username]
                if len(ch_df) == 0:
                    continue
                else:
                    ch_df.drop(columns=["raspi_name"], inplace=True)
                    ch_df[["chID", "writeKey"]] = [ch_ID, write_key]
                    return_df = pd.concat([return_df, ch_df], axis = 0, ignore_index = True)
            
            return return_df

    
    def fetch_ambient_read_config(self):
        # Ambientから読み込むための設定を読み込む
        return_df = pd.DataFrame(columns=["house_name", "chID", "dataID", "readKey", "datatype"])

        for i in self.chInfo_df.index:
            ch_num = self.chInfo_df.loc[i, "chNumber"] 
            ch_ID = self.chInfo_df.loc[i, "chID"]
            read_key = self.chInfo_df.loc[i, "readKey"]
            if (ch_ID == None) or (read_key == None):
                continue
            else:
                ch_df = self.convert_excelsheet_into_df(self.wb[f"{ch_num}"])
                # ラズパイのユーザー名に依存して送信するデータのIDを指定する。
                ch_df.dropna(inplace = True)
                
                if len(ch_df) == 0:
                    continue
                else:
                    ch_df.drop(["raspi_name", "sensor_name"], axis = 1, inplace = True)
                    ch_df[["chID", "readKey"]] = [ch_ID, read_key]
                    return_df = pd.concat([return_df, ch_df], axis = 0, ignore_index = True)
            
            return return_df