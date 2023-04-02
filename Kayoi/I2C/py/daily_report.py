# 日報を作成する

import pandas as pd  # pandasをインポートする
import datetime
from decimal import Decimal, ROUND_HALF_UP  # 四捨五入に用いる
import math  # 主にisnanのため

import os
import re
import requests
from Read_csv import Read_csv
from get_filepath import get_filepath
from recieve_username_auth import recieve_username_auth

import matplotlib.pyplot as plt  # グラフを描画するのに用いる
import matplotlib.dates as mdates  # 軸ラベルの表記を時間のみに直す
import seaborn as sns  # グラフをきれいに見せる



class Daily_report():
    def __init__(self):

        self.date = datetime.date.today() - datetime.timedelta(days=1)

        # テスト用に以下の日付を使用
        # self.date = datetime.date.today()
        # self.date = datetime.date(2022,9,1)
        self.date_str = self.date.strftime('%Y年%m月%d日')
        self.url99 = "https://notify-api.line.me/api/notify"

    # 先に整理しておくべき関数群

    def convert_to_float(self, data):
        try:
            data = float(data)
        except ValueError:
            print("ValueError")
            data = math.nan
        return data

    def draw_single_ax_graph(self, graphID):

        # グラフを描くスペースの宣言
        fig, ax = plt.subplots()

        datatype = self.graph_datatype_dict[graphID][0]

        ylim_low_threshold = self.datatype_yilm_low_dict[datatype]
        ylim_low = ylim_low_threshold

        ylim_high_threshold = self.datatype_yilm_high_dict[datatype]
        ylim_high = ylim_high_threshold

        counter_list = []
        for house in self.house_list:
            house_df = self.house_df_dict[house]
            if not datatype in house_df.columns:
                counter_list.append(0)
                continue

            house_ser = self.house_df_dict[house][datatype]
            # 描画するデータがない場合はスキップする
            if len(house_ser.dropna()) == 0:
                counter_list.append(0)
                continue
            else:
                counter_list.append(1)
            # ax座標の指定
            treat_ax = ax
            # プロット

            house_ser = house_ser.dropna()

            treat_ax.plot(
                house_ser, color=self.cmap_dict[datatype], marker=self.marker_dict[house], markerfacecolor="white", ls=self.ls_dict[house])
            # x軸の上限下限を最小から最大までに設定
            treat_ax.set_xlim([house_ser.index[0], house_ser.index[-1]])
            # y軸は基本、警告限界までとしつつ、超えたらその分伸ばして枠内に描画できるように対応
            ylim_low = min(min(house_ser.values), ylim_low)
            ylim_high = max(max(house_ser.values), ylim_high)

            margin = (ylim_high - ylim_low) / 10
            treat_ax.set_ylim([ylim_low - margin, ylim_high + margin])
            if ylim_low != ylim_low_threshold:
                treat_ax.hlines(
                    ylim_low_threshold, xmin=house_ser.index[0], xmax=house_ser.index[-1], colors="red")
            if ylim_high != ylim_high_threshold:
                treat_ax.hlines(
                    ylim_high_threshold, xmin=house_ser.index[0], xmax=house_ser.index[-1], colors="red")

        if not any(counter_list):
            return
        else:
            # x軸ラベルの標記をHH:MMに設定
            # treat_ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
            # HH時の方がすっきりして見やすかったのでこちらに設定
            treat_ax.xaxis.set_major_formatter(mdates.DateFormatter("%H時"))
            # y軸ラベルを設定
            unit = self.datatype_unit_dict[datatype]
            # 単位が設定されていない場合にnanが表示されるのを防ぐ
            if isinstance(unit, str) == True:
                ylabel = datatype + "\n" + "(" + str(unit) + ")"
            else:
                ylabel = datatype

            treat_ax.set_ylabel(
                ylabel, labelpad=6, rotation="horizontal", horizontalalignment="right")
            # 凡例を表示
            # house_legend_df = pd.DataFrame([self.house_list, counter_list]).T
            # house_legend_list = list(house_legend_df[house_legend_df[1] == 1][0])
            house_legend_list = [house for house, counter in zip(
                self.house_list, counter_list) if counter == 1]
            treat_ax.legend(house_legend_list, ncol=len(
                house_legend_list), bbox_to_anchor=(0., 1.02, 1., 0.102), loc=3)

            fig.suptitle(f"{self.date_str}における{datatype}の推移")

            # 保存
            file = f"../graph/graph{graphID}.png"
            fig.savefig(get_filepath(file), format="png", dpi=100,
                        bbox_inches="tight", pad_inches=0.05)
            print(f"{graphID}終了")

    def draw_multi_ax_graph(self, house, graphID):

        # 描画するグラフの数
        num = len(self.graph_datatype_dict[graphID])
        # 平方根の切り上げを一辺の数とすることで、もれなく描画することを可能とする
        side = math.ceil(math.sqrt(num))

        # x軸方向の数
        ax_x_num = side
        # y軸方向の数
        # 不要なaxesを出さないようにしている
        ax_y_num = math.ceil(num/side)
        # subplotで与えられるaxesの数
        ax_num = ax_x_num * ax_y_num

        # グラフを発生させる
        fig, ax = plt.subplots(ax_y_num, ax_x_num)
        plt.subplots_adjust(left=-0.5, wspace=0.3)

        # 与えられたaxesに対してforを回す
        for i in range(ax_num):
            # イメージ: [0,1,2]\n[3,4,5]\n[6,7,8]
            ax_x = i % side
            ax_y = i // side
            # 描画する数を超えるなら、axesを削除する
            if (i+1) <= num:
                print(ax_x, ax_y)
                # ax座標の指定
                if num <= 2:
                    treat_ax = ax[ax_x]
                else:
                    treat_ax = ax[ax_y, ax_x]

                # 数値の読み込み
                datatype = self.graph_datatype_dict[graphID][i]
                house_df = self.house_df_dict[house]
                if not datatype in house_df.columns:
                    treat_ax.remove()
                    continue

                house_ser = self.house_df_dict[house][datatype]

                # 描画するデータがない場合はそのaxesを削除
                if len(house_ser.dropna()) == 0:
                    treat_ax.remove()
                    continue
                # プロット
                house_ser = house_ser.dropna()
                treat_ax.plot(
                    house_ser, color=self.cmap_dict[datatype], marker=self.marker_dict[house], markerfacecolor="white", ls=self.ls_dict[house])
                # x軸の上限下限を最小から最大までに設定
                treat_ax.set_xlim([house_ser.index[0], house_ser.index[-1]])
                # y軸は基本、警告限界までとしつつ、超えたらその分伸ばして枠内に描画できるように対応
                ylim_low_threshold = self.datatype_yilm_low_dict[datatype]
                ylim_low = min(ylim_low_threshold, min(house_ser.values))
                ylim_high_threshold = self.datatype_yilm_high_dict[datatype]
                ylim_high = max(ylim_high_threshold, max(house_ser.values))
                margin = (ylim_high - ylim_low) / 10
                treat_ax.set_ylim([ylim_low - margin, ylim_high + margin])
                if ylim_low != ylim_low_threshold:
                    treat_ax.hlines(
                        ylim_low_threshold, xmin=house_ser.index[0], xmax=house_ser.index[-1], colors="red")
                if ylim_high != ylim_high_threshold:
                    treat_ax.hlines(
                        ylim_high_threshold, xmin=house_ser.index[0], xmax=house_ser.index[-1], colors="red")

                # x軸ラベルの標記をHH:MMに設定
                # treat_ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
                # HH時の方がすっきりして見やすかったのでこちらに設定
                treat_ax.xaxis.set_major_formatter(mdates.DateFormatter("%H時"))
                # y軸ラベルを設定
                unit = self.datatype_unit_dict[datatype]
                # 単位が設定されていない場合にnanが表示されるのを防ぐ
                if isinstance(unit, str) == True:
                    ylabel = datatype + "\n" + "(" + str(unit) + ")"
                else:
                    ylabel = datatype
                treat_ax.set_ylabel(
                    ylabel, labelpad=6, rotation="horizontal", horizontalalignment="right")
            else:
                ax[ax_y, ax_x].remove()

        fig.suptitle(f"{self.date_str}における{house}内の環境データの推移")

        file = f"../graph/graph{graphID}_{house}.png"
        fig.savefig(get_filepath(file), format="png", dpi=100,
                    bbox_inches="tight", pad_inches=0.05)
        print(f"{graphID}_{house}終了")
    # ここまで。

    def set_df(self):
        # 必要なDF関連は全てここで読み込んで用意してしまう
        file = "../resource/I2C_data_period.csv"
        filepath = get_filepath(file)
        try:
            with Read_csv(filepath) as df:
                data_df = df
        except FileNotFoundError:
            message = "WioNodeから得たデータを記録したファイルが存在しません"
            file = "../stderr.log"
            filepath = get_filepath(file)
            with open(filepath, mode = "a") as f:
                f.write(message + "\n")
            return

        data_df["datetime"] = pd.to_datetime(data_df["datetime"])
        data_df.loc[:, "date"] = list(
            map(lambda x: x.date(), data_df["datetime"]))

        data_df = data_df[data_df["date"] == self.date]

        # ハウスで分ける
        # 何をするにしても、ハウスを分けないと始まらないはず
        self.house_list = list(dict.fromkeys(data_df["house_name"]))
        self.house_df_dict = {}
        for house in self.house_list:
            house_data_df = data_df.loc[data_df["house_name"] == house, :]

            datatype_set = list(dict.fromkeys(data_df["datatype"]))
            house_data_df = house_data_df.pivot(
                index=["datetime"], columns="datatype", values="value")
            house_data_df.columns.name = None
            house_data_df = house_data_df.sort_index()

            for datatype in datatype_set:
                data_ser = house_data_df.loc[:, datatype].copy()
                # エラーなどで数値以外が入っていた時の対処
                data_ser = data_ser.map(self.convert_to_float)
                data_ser.interpolate(inplace=True)
                data_ser = data_ser.astype("float32")
                house_data_df[datatype] = data_ser

            self.house_df_dict[house] = house_data_df

        # グラフ関連
        file = "../resource/graph_datatype_setting.csv"
        filepath = get_filepath(file)
        try:
            with Read_csv(filepath) as df:
                graph_datatype_df = df
        except FileNotFoundError:
            message = "グラフ表示に関する情報をまとめたファイルが存在しません"
            file = "../stderr.log"
            filepath = get_filepath(file)
            with open(filepath, mode = "a") as f:
                f.write(message + "\n")
            return
        pattern = re.compile(r'データの種類\d*')
        col_list = [col for col in graph_datatype_df.columns if re.search(
            pattern, col) != None]
        treat_df = graph_datatype_df[col_list]

        self.graph_datatype_set_list = list(
            set(treat_df.melt()["value"].dropna()))

        # dictにgraphIDをキーとして、使用するデータの種類のリストを格納する
        self.graph_datatype_dict = {row["グラフID"]: list(
            row.dropna().drop("グラフID")) for _, row in graph_datatype_df.iterrows()}
        #全グラフにおける共通設定

        #色
        cmap = plt.get_cmap("viridis")
        # ここ、cmapが0-1の範囲ならば、index/len(list)-1の方が良くないか
        # 現状、4通りの場合、0/4, 1/4, 2/4, 3/4 になっている (4/4が使えていない)
        self.cmap_dict = {datatype: cmap(self.graph_datatype_set_list.index(
            datatype) / len(self.graph_datatype_set_list)) for datatype in self.graph_datatype_set_list}

        # マーカー
        # ハウスによって種類を分ける
        marker_list = ["o", "^", "s", "D", "v"]
        self.marker_dict = {house: marker_list[i % len(
            marker_list)] for i, house in enumerate(self.house_list)}

        # line_style
        # ハウスによって線の種類を分ける
        # マーカーと合わせて、5*4=20種類のグラフを描き分ける
        ls_list = ["solid", "dotted", "dashed", "dashdot"]
        self.ls_dict = {house: ls_list[i % len(
            ls_list)] for i, house in enumerate(self.house_list)}

        # 単位・上限・下限の辞書作成
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

        self.datatype_unit_dict = {row["データの種類"]: row["単位"]
                                   for _, row in datatype_setting_df.iterrows()}
        self.datatype_yilm_low_dict = {
            row["データの種類"]: row["下限閾値"] for _, row in datatype_setting_df.iterrows()}
        self.datatype_yilm_high_dict = {
            row["データの種類"]: row["上限閾値"] for _, row in datatype_setting_df.iterrows()}

        # datatype_list = list(datatype_setting_df["データの種類"].values)
        # unit_list = list(datatype_setting_df["単位"].values)

        # datatype_yilm_low_list = list(datatype_setting_df["下限閾値"].values)
        # datatype_yilm_high_list = list(datatype_setting_df["上限閾値"].values)

        # for datatype,datatype_unit,datatype_yilm_low,datatype_yilm_high in zip(datatype_list, unit_list,datatype_yilm_low_list,datatype_yilm_high_list):
        #     self.datatype_unit_dict[datatype] = datatype_unit
        #     self.datatype_yilm_low_dict[datatype] = datatype_yilm_low
        #     self.datatype_yilm_high_dict[datatype] = datatype_yilm_high

        # LINEのアクセストークンの管理
        file = "../resource/line_token.csv"
        filepath = get_filepath(file)
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

        self.line_token_list = list(line_token_df[(line_token_df["通知目的"] == (
            "全般")) | (line_token_df["通知目的"] == ("日報"))]["アクセストークン"])

    def make_graph(self):
        sns.set()
        sns.set_theme(style="whitegrid", font="Noto Sans JP", font_scale=1.5)
        plt.rcParams['xtick.direction'] = 'in'  # x axis in
        plt.rcParams['ytick.direction'] = 'in'  # y axis in
        plt.rcParams["legend.frameon"] = True
        plt.rcParams["legend.fancybox"] = False
        plt.rcParams["legend.framealpha"] = 1  # 透明度の指定、0で塗りつぶしなし
        plt.rcParams["legend.edgecolor"] = 'black'  # edgeの色を変更
        plt.rcParams["legend.handlelength"] = 1  # 凡例の線の長さを調節
        plt.rcParams["legend.labelspacing"] = 0.5  # 垂直方向（縦）の距離の各凡例の距離
        plt.rcParams["legend.handletextpad"] = 0.2  # 凡例の線と文字の距離の長さ
        plt.rcParams["legend.markerscale"] = 1  # 点がある場合のmarker scale
        plt.rcParams["legend.borderaxespad"] = 0.5
        plt.rcParams["figure.figsize"] = (10, 10)
        plt.rcParams["figure.dpi"] = 100
        # グラフ描画本体
        for graphID in self.graph_datatype_dict:
            graph_datatype_list = self.graph_datatype_dict[graphID]
            graph_num = len(graph_datatype_list)
            if graph_num == 1:
                # ハウス間対立
                # グラフ数1
                self.draw_single_ax_graph(graphID)
            else:
                # ハウスごとに描画
                for house in self.house_list:
                    self.draw_multi_ax_graph(house, graphID)

    def cal_mmm(self):
        # 最高値・平均値・最低値を算出する
        self.mmm_df_dict = {}
        for house in self.house_list:

            house_df = self.house_df_dict[house]
            # treat_df = house_df[self.graph_datatype_set_list]
            treat_df = house_df

            max_ser = treat_df.max()
            max_ser = pd.Series(map(lambda x: Decimal(str(x)).quantize(
                Decimal('0.1'), rounding=ROUND_HALF_UP), max_ser), index=max_ser.index)
            mean_ser = treat_df.mean()
            mean_ser = pd.Series(map(lambda x: Decimal(str(x)).quantize(
                Decimal('0.1'), rounding=ROUND_HALF_UP), mean_ser), index=mean_ser.index)
            min_ser = treat_df.min()
            min_ser = pd.Series(map(lambda x: Decimal(str(x)).quantize(
                Decimal('0.1'), rounding=ROUND_HALF_UP), min_ser), index=min_ser.index)

            mmm_df = pd.DataFrame([min_ser, mean_ser, max_ser], index=[
                                  "min", "mean", "max"])
            mmm_df.loc[:, "mmm"] = ["min", "mean", "max"]
            mmm_df.loc[:, "ハウス名"] = house
            mmm_df.loc[:, "日付"] = self.date

            self.mmm_df_dict[house] = mmm_df

            file = f"../resource/mmm_{house}.csv"
            filepath = get_filepath(file)
            # has_file = os.path.isfile(filepath)
            # # 無ければつくる、あれば読み込む
            # if has_file == False:
            #     df_mmm_to_csv = pd.DataFrame(columns = mmm_df.columns)
            # else:
            #     df_mmm_to_csv = pd.read_csv(filepath, encoding="shift-jis")
            # # 結合
            # df_mmm_to_csv = pd.concat([df_mmm_to_csv, mmm_df])
            # # 出力
            # df_mmm_to_csv.to_csv(filepath, encoding="shift-jis", index = False)
            mmm_df.to_csv(filepath, mode="a", encoding="shift-jis",
                          index=False, header=not os.path.exists(filepath))

    def notify_line_main(self, message, graph, token):
        payload = {'message': message}
        files = {"imageFile": graph}

        headers = {'Authorization': 'Bearer ' + token}
        r = requests.post(self.url99, data=payload,
                          headers=headers, files=files)
        print(message)

    def notify_line(self):
        for graphID in self.graph_datatype_dict:
            graph_datatype_list = self.graph_datatype_dict[graphID]
            if len(graph_datatype_list) == 0:
                # 空欄
                continue
            elif len(graph_datatype_list) == 1:
                # 単数
                # グラフ1枚に複数ハウスのデータが乗ってくる
                # グラフを乗せる→ハウスA→ハウスB→……
                datatype = graph_datatype_list[-1]
                message = "\n"
                for house in self.house_list:
                    house_df = self.mmm_df_dict[house]
                    if not datatype in house_df.columns:
                        continue
                    house_min = house_df.loc[house_df["mmm"]
                                             == "min", datatype].iloc[-1]
                    house_mean = house_df.loc[house_df["mmm"]
                                              == "mean", datatype].iloc[-1]
                    house_max = house_df.loc[house_df["mmm"]
                                             == "max", datatype].iloc[-1]
                    # データがない場合は通知文を省く
                    if any([math.isnan(house_min), math.isnan(house_mean), math.isnan(house_max)]):
                        pass
                    else:
                        # 単位
                        unit = self.datatype_unit_dict[datatype]
                        # 単位無しの場合の処理
                        if isinstance(unit, str) == False:
                            if math.isnan(unit) == True:
                                unit = ""
                        message += "★" + str(house) + '\n'
                        message += '最低' + datatype + ": " + \
                            str(house_min) + " " + unit + '\n'
                        message += '平均' + datatype + ": " + \
                            str(house_mean) + " " + unit + '\n'
                        message += '最高' + datatype + ": " + \
                            str(house_max) + " " + unit + '\n'
                if message == "\n":
                    continue
                # 通知を行う。多分関数にまとめてやった方が良さそう
                for token in self.line_token_list:
                    file = f"../graph/graph{graphID}.png"
                    with open(get_filepath(file), "rb") as graph:
                        self.notify_line_main(message, graph, token)
            else:
                # 2個以上
                #  グラフは1枚
                graph_datatype_list = self.graph_datatype_dict[graphID]
                for house in self.house_list:
                    message = "\n"
                    for datatype in graph_datatype_list:
                        if not datatype in house_df.columns:
                            continue
                        house_df = self.mmm_df_dict[house]
                        house_min = house_df.loc[house_df["mmm"]
                                                 == "min", datatype].iloc[-1]
                        house_mean = house_df.loc[house_df["mmm"]
                                                  == "mean", datatype].iloc[-1]
                        house_max = house_df.loc[house_df["mmm"]
                                                 == "max", datatype].iloc[-1]
                        # データがない場合は通知文を省く
                        if any([math.isnan(house_min), math.isnan(house_mean), math.isnan(house_max)]):
                            pass
                        else:
                            # 単位
                            unit = self.datatype_unit_dict[datatype]
                            # 単位無しの場合の処理
                            if isinstance(unit, str) == False:
                                if math.isnan(unit) == True:
                                    unit = ""
                            message += "★" + str(house) + '\n'
                            message += '最低' + datatype + ": " + \
                                str(house_min) + " " + unit + '\n'
                            message += '平均' + datatype + ": " + \
                                str(house_mean) + " " + unit + '\n'
                            message += '最高' + datatype + ": " + \
                                str(house_max) + " " + unit + '\n'
                    if message == "\n":
                        continue
                    for token in self.line_token_list:
                        file = f"../graph/graph{graphID}_{house}.png"
                        with open(get_filepath(file), "rb") as graph:
                            self.notify_line_main(message, graph, token)


def main():
    if recieve_username_auth():        
        # インスタンス宣言
        daily_report = Daily_report()

        daily_report.set_df()
        daily_report.make_graph()
        daily_report.cal_mmm()
        daily_report.notify_line()


if __name__ == "__main__":
    main()
