# gzip を用いて圧縮する
# 1週間に1度程度実行する想定。
# 日報作成後に実行することで、日報作成に影響を与えないで済むかと思われる。

# 毎週月曜日の1時4分に実行
# 4 1 * * 1

# in_file & in_filepath: 入力ファイルのパスとその絶対パス
# out_file & out_filepath: 出力ファイルのパスとその絶対パス
# td: 今日の日付
# split_day & split_time & split_datetime: 日付、時刻、日時を分割 (1日前の 23:59:59)
# in_df: csv ファイルから読み込んだ入力データフレーム
# out_df: `split_datetime` までのレコードを保存するデータフレーム
# header: 出力ファイルにヘッダを追加するかどうか (ファイルが存在しない場合は True)

import os
import datetime
import pandas as pd
from get_filepath import get_filepath
from Read_csv import Read_csv
from recieve_username_auth import recieve_username_auth

if recieve_username_auth():
    in_file_list = ["../resource/I2C_data_period.csv", "../resource/I2C_data_local.csv"]
    out_file_list = ["../resource/I2C_data_period.gz", "../resource/I2C_data_local.gz"]

    for in_file, out_file in zip(in_file_list, out_file_list):
        in_filepath = get_filepath(in_file)
        out_filepath = get_filepath(out_file)

        try:
            in_df = pd.read_csv(in_filepath, encoding = "shift-jis", index_col = False, header = 0)
        except FileNotFoundError as e:
            message = "WioNodeから得たデータを記録したファイルが存在しません"
            file = "../stderr.log"
            filepath = get_filepath(file)
            with open(filepath, mode = "a") as f:
                f.write(message + "\n")
            break

        td = datetime.date.today()
        # td = datetime.date(2023, 1, 9)

        split_day = td - datetime.timedelta(days=1)
        split_time = datetime.time(23, 59, 59)
        split_datetime = datetime.datetime.combine(split_day, split_time)

        in_df.loc[:, "datetime"] = pd.to_datetime(in_df.loc[:, "datetime"])
        out_df = in_df.loc[in_df["datetime"] <= split_datetime, :]

        # ファイルが既に存在するならヘッダー無し
        out_df.to_csv(
            out_filepath,
            index=False,
            header=not os.path.exists(out_filepath),
            compression="gzip",
            encoding="shift-jis",
            mode="a")

        # in_fileの方には、アーカイブした部分を削除したdfを保存する。
        in_df = in_df.loc[in_df["datetime"] > split_datetime, :]
        in_df.to_csv(in_filepath, encoding="shift-jis", index=False)