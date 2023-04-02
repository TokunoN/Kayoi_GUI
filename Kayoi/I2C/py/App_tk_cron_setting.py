# cronの設定を入力するためのGUIアプリケーション
# tk版

from get_filepath import get_filepath
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox as mb
import pandas as pd
import os

class App(ttk.Frame):
    def __init__(self, master = None):
        super().__init__(master)
        # ウィンドウを閉じたときに保存するかどうか尋ねるようにする
        self.master.protocol("WM_DELETE_WINDOW", self.ask_save)
        self.master.title("cron設定")

        file = "../resource/cron_setting.csv"
        self.df_filepath = get_filepath(file)

        self.index_list = ["data_getting", "notify_period", "notify_alert", "data_receiving"]

        if os.path.exists(self.df_filepath):
            self.df = pd.read_csv(self.df_filepath, header=0, index_col=0, encoding="shift-jis")
        else:
            self.df = pd.DataFrame(
                [[True, 5] for i in range(4)],
                columns=["run_flag", "run_span"],
                index = self.index_list)
        
        file = "../resource/daily_report_run_flag.txt"
        self.daily_report_run_flag_filepath = get_filepath(file)
        try:
            with open(self.daily_report_run_flag_filepath, encoding="shift-jis", mode = "r") as f:
                daily_report_run_flag = True if f.read() == "True" else False
        # 初期設定としてはTrue
        except FileNotFoundError:
            daily_report_run_flag = True

        file = "../resource/receive_username.txt"
        self.receive_username_filepath = get_filepath(file)
        try:
            with open(self.receive_username_filepath, encoding="shift-jis", mode = "r") as f:
                receive_username = f.read()
        except FileNotFoundError:
            receive_username = ""

        self.title_text_list = [
        "センサーからデータを取得する間隔",
        "警報を通知する間隔",
        "定期的にデータを通知する間隔",
        "Ambientからデータを取得する間隔",
        "日報作成の可否",
        "Ambientからデータを取得する"+"\n"+"ラズパイのユーザー名"
        ]
        cronsetrow_list = ["data_getting", "notify_alert", "notify_period", "data_receiving"]
        option_list = [5, 10, 15, 20, 30, 60, 120]


        # センサーからデータを取得する間隔
        # 警報を通知する間隔
        # 定期的にデータを通知する間隔
        # Ambientからデータを取得する間隔
        self.check_bv_dict = {}
        self.check_dict = {}

        self.title_text_dict = {}
        self.combo_sv_dict = {}
        self.combo_dict = {}

        for i, cronsetrow in enumerate(cronsetrow_list):
            row_frame = ttk.Frame(master)
            self.check_bv_dict[i] = tk.BooleanVar(value=bool(self.df.loc[cronsetrow, "run_flag"]))
            self.check_dict[i] = tk.Checkbutton(row_frame, variable=self.check_bv_dict[i], onvalue=1, offvalue=0)

            self.title_text_dict[i] = ttk.Label(row_frame, text = self.title_text_list[i], width=30)
            colon = ttk.Label(row_frame, text=" : ")

            self.combo_sv_dict[i] = tk.StringVar(value=str(self.df.loc[cronsetrow, "run_span"]))
            self.combo_dict[i] = ttk.Combobox(row_frame, textvariable=self.combo_sv_dict[i], values=option_list, width=5)

            self.check_dict[i].grid(row = 0, column=0)
            self.title_text_dict[i].grid(row = 0, column=1)
            colon.grid(row = 0, column=2)
            self.combo_dict[i].grid(row=0, column=3)

            row_frame.pack(fill=tk.X)
        
        # 日報作成の可否
        i += 1
        row_frame = ttk.Frame(master)
        self.check_bv_dict[i] = tk.BooleanVar(value=daily_report_run_flag)
        self.check_dict[i] = tk.Checkbutton(row_frame, variable=self.check_bv_dict[i], onvalue=1, offvalue=0)
        self.title_text_dict[i] = ttk.Label(row_frame, text = self.title_text_list[i], width=30)
        self.check_dict[i].grid(row = 0, column=0)
        self.title_text_dict[i].grid(row = 0, column=1)
        row_frame.pack(fill=tk.X)

        # Ambientからデータを取得する"+"\n"+"ラズパイのユーザー名
        i += 1
        row_frame = ttk.Frame(master)
        self.empty_label = ttk.Label(row_frame, text = "", width = 4)
        self.title_text_dict[i] = ttk.Label(row_frame, text = self.title_text_list[i], width=30)
        colon = ttk.Label(row_frame, text=" : ")

        self.entry_sv = tk.StringVar(value=receive_username)
        self.entry = ttk.Entry(row_frame, textvariable=self.entry_sv, width=8)

        self.empty_label.grid(row = 0, column=0)
        self.title_text_dict[i].grid(row = 0, column=1)
        colon.grid(row = 0, column=2)
        self.entry.grid(row=0, column=3)

        row_frame.pack(fill=tk.X)


    def save(self):
        # 入力されたテキストをファイルに保存する関数
        for i in range(0,6):
            if i < 4:
                self.df.loc[self.index_list[i], "run_flag"] = self.check_bv_dict[i].get()
                self.df.loc[self.index_list[i], "run_span"] = self.combo_sv_dict[i].get()
            elif i == 4:
                with open(self.daily_report_run_flag_filepath, encoding="shift-jis", mode = "w") as f:
                    f.write(str(self.check_bv_dict[i].get()))
            else:
                receive_username = self.entry_sv.get()
                with open(self.receive_username_filepath, encoding="shift-jis", mode = "w") as f:
                    f.write(receive_username)

        self.df.to_csv(self.df_filepath, header=True, index=True, encoding="shift-jis")
        
        mb.showinfo(title = "変更を保存しました",message="この後、ラズパイ上でcron設定プログラムを実行してください")

        self.master.destroy()

    def ask_save(self):
        # ウィンドウを閉じる前に保存するかどうかを尋ねる関数
        answer = mb.askyesnocancel("Save", "保存して終了しますか？")
        if answer:
            self.save()
        elif answer == False:
            self.master.destroy()
        else:
            pass

root = tk.Tk()
app = App(master=root)
app.mainloop()