# Ambient から定期的にデータを取得する

from AmbientDataHandler import AmbientDataHandler
import datetime
from get_filepath import get_filepath
import pandas as pd
import ambient
import os
from recieve_username_auth import recieve_username_auth

def main():
    adh = AmbientDataHandler()
    read_config_df = adh.fetch_ambient_read_config()
    chID_readKey_df = read_config_df[["chID", "readKey"]]
    # chID_set =  set(chID_readKey_df["chID"])

    all_read_data_df = pd.DataFrame(columns=["created","chID"] + list(set(read_config_df["dataID"])))
    datetime_now = datetime.datetime.now()

    # 最後に読み込みを行った日時を読み込む。
    # そこを起点として新しいデータを読み込む。
    file = "../resource/latest_read_datetime.txt"
    filepath = get_filepath(file)
    try:
        with open(filepath, encoding="shift-jis", mode = "r") as f:
            latest_read_datetime = f.read()
    except FileNotFoundError:
        # 最終読み込み時刻を保存したファイルが無ければ、読み込み間隔を取得し、その分を引いた時刻を起点とする
        # それが見つからなければエラーを返す
        file = "../resource/cron_setting.csv"
        filepath = get_filepath(file)
        try:
            cron_setting_df = pd.read_csv(filepath, encoding="shift-jis", index_col=0)
        except FileNotFoundError:
            message = "最後に読み込みを行った時刻を保存したファイルが存在しません"
            file = "../stderr.log"
            filepath = get_filepath(file)
            with open(filepath, mode = "a") as f:
                f.write(message + "\n")
            return
        data_getting_run_span = int(cron_setting_df.loc["data_getting", "run_span"])
        latest_read_datetime = (datetime_now - datetime.timedelta(minutes=data_getting_run_span)).strftime("%Y-%m-%d %H:%M:%S")

    start_date_time = latest_read_datetime
    end_date_time = datetime_now.strftime("%Y-%m-%d %H:%M:%S")

    for chID in set(chID_readKey_df["chID"]):
        # chIDが同じなら一意にreadKeyが決まるはず。
        readKey = set(chID_readKey_df.loc[chID_readKey_df["chID"] == chID, "readKey"]).pop()

        # WriteKeyは使わないので ""でよい。
        am = ambient.Ambient(chID,"", readKey)
        read_data = am.read(start = start_date_time, end = end_date_time)
        read_data_df = pd.DataFrame(read_data)
        read_data_df["chID"] = chID
        all_read_data_df = pd.concat([all_read_data_df, read_data_df], axis = 0)
        
    # all_read_data_dfが空 = 更新するデータが無い.
    # よって、以後の処理を行わない。 
    if all_read_data_df.empty:
        print("No data to read")
        return

    all_read_data_df = all_read_data_df.rename(columns={"created": "datetime"})
    # Ambient から帰ってくる日付はUTC
    all_read_data_df["datetime"] = pd.to_datetime(all_read_data_df["datetime"]).dt.tz_convert('Asia/Tokyo')
    # ここから後でtimezoneの情報はいらないと思うので消す。
    all_read_data_df["datetime"] = list(map(lambda x: x.replace(tzinfo = None).strftime("%Y-%m-%d %H:%M:%S"), all_read_data_df["datetime"]))

    melted_df = all_read_data_df.melt(id_vars=["datetime", "chID"], var_name="dataID")
    # chIDとdataIDをキーとしてdatatyoeとhouse_nameの情報を列に追加する。
    update_dict = {
        (row["chID"], row["dataID"]): (row["datatype"], row["house_name"])
        for _, row in read_config_df.iterrows()
    }
    melted_df[["datatype", "house_name"]] = melted_df.apply(lambda x: update_dict.get((x["chID"], x["dataID"]), (None, None)), axis=1, result_type="expand")
    melted_df = melted_df.drop(columns=["chID", "dataID"])
    melted_df = melted_df.reindex(columns=["datetime", "house_name", "datatype", "value"])

    file = "../resource/I2C_data_period.csv"
    filepath = get_filepath(file)
    melted_df.to_csv(filepath, mode="a", encoding="shift-jis", header = not os.path.exists(filepath), index=False)

    # 読み込んだデータの中で最新のものを抜きだし、定期通知用に記録する。
    latest_df = pd.DataFrame()
    house_datatype_tuple_list = melted_df[["house_name", "datatype"]].apply(tuple, axis=1).drop_duplicates().tolist()
    for house_datatype_tuple in house_datatype_tuple_list:
        house_datatype_df = melted_df.loc[(melted_df["house_name"] == house_datatype_tuple[0]) & (melted_df["datatype"] == house_datatype_tuple[1]), :]
        latest_datetime = max(house_datatype_df["datetime"])
        concat_df = house_datatype_df.loc[house_datatype_df["datetime"] == latest_datetime, :]
        latest_df = pd.concat([latest_df, concat_df], axis = 0)

    file = "../resource/I2C_data_latest_period.csv"
    filepath = get_filepath(file)
    latest_df.to_csv(filepath, mode="w", encoding="shift-jis", header = True, index=False)

    # データの保存が無事終了してから、最終読み込み日時を書き込む
    # 読み込み日時が更新されない＝どこかでエラー発生
    # 次に読み込む時に、保存できなかった分のデータも一緒に読み込む
    file = "../resource/latest_read_datetime.txt"
    filepath = get_filepath(file)
    with open(filepath, encoding="shift-jis", mode = "w") as f:
        f.write(end_date_time)

if recieve_username_auth():
    main()