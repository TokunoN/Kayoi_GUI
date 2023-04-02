# LINE通知用のGUIアプリケーション
# tk版

from get_filepath import get_filepath
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox as mb
import pandas as pd
import math

class App(ttk.Frame):
    def __init__(self, master = None):
        super().__init__(master)
        self.master.title("App_tk_LINE_Notify_setting")
        # self.master.geometry("150x150")

        button_name_list = [
            "LINE_Notifyの設定",
            "データの種類の設定",
            "グラフの設定"
        ]
        for button_name in button_name_list:
            ttk.Button(self.master, text=button_name, command=lambda button_name = button_name: self.open_form(button_name)).pack(padx=5, pady=5)

    def open_form(self, button_name):
        self.form_window = FormWindow(self, button_name)
        self.form_window.grab_set()
        self.form_window.focus_set()
        self.form_window.protocol("WM_DELETE_WINDOW", self.form_window.ask_save)


class FormWindow(tk.Toplevel):
    def __init__(self, master, button_name):
        super().__init__(master=None)
        self.title("Form_Window")
        # self.geometry は指定しないことで可動的になるっぽい

        self.file_dict = {
            "LINE_Notifyの設定"  : "../resource/line_token.csv",
            "データの種類の設定" : "../resource/datatype_setting.csv",
            "グラフの設定"       : "../resource/graph_datatype_setting.csv"
            }
        file = self.file_dict[button_name]
        self.filepath = get_filepath(file)
        try:
            self.df = pd.read_csv(self.filepath, header = None, index_col=False, encoding="shift-jis")
        except FileNotFoundError:
            col_list_dict = {
                "LINE_Notifyの設定"  : ['アクセストークン', 'LINEのグループ名', '通知目的'],
                "データの種類の設定" : ['データの種類', '単位', '下限警告文', '上限警告文', '下限閾値', '上限閾値'],
                "グラフの設定"       : ['グラフID', 'データの種類1', 'データの種類2', 'データの種類3', 'データの種類4']
            }
            col_list = col_list_dict[button_name]
            self.df = pd.DataFrame(
                [col_list] + 
                [["" for _ in col_list] for _ in range(5)]
            )

        def nan_and_None_to_empty(cell):
            # データが無い場合に空白表示にする
            if isinstance(cell, str) == False:
                if cell == None:
                    cell = ""
                elif math.isnan(cell):
                    cell = ""
            return str(cell)

        self.entry_frame = tk.Frame(self)
        self.sv_list = [
            [
                tk.StringVar(value = nan_and_None_to_empty(cell)) for cell in row
            ] for _,row in self.df.iterrows()
        ]
        self.entry_list = [[tk.Entry(
            self.entry_frame,
            textvariable=sv,
            state="readonly" if i == 0 else "normal",
            justify="center" if i == 0 else "left",
            width = 15
        ) for _, sv in enumerate(row)
        ] for i, row in enumerate(self.sv_list)]
        [[entry.grid(row=i, column=j) for j, entry in enumerate(row)]
         for i, row in enumerate(self.entry_list)]
        self.entry_frame.pack(anchor="nw", padx=10, pady = 10)

        self.add_entry_row_button = tk.Button(self, text="行追加", command=self.add_entry_row)
        self.add_entry_row_button.pack(anchor="nw", padx=10, pady = 10)

    def add_entry_row(self):
        # エントリーの表の下に「追加」ボタンを配置。
        # 押下時に表に空行を追加する
        # 空行がたくさん生まれると想定されるので、save時に空行削除を仕込む
        self.sv_list.append([tk.StringVar(value="") for _ in range(len(self.df.columns))])
        self.entry_list.append([
            tk.Entry(
            self.entry_frame,
            textvariable=sv,
            state = "normal",
            justify = "left",
            width = 15
            ) for sv in self.sv_list[-1]
        ]
        )
        [entry.grid(row=len(self.entry_list), column=j) for j, entry in enumerate(self.entry_list[-1])]

    def save(self):
        # 入力されたテキストをファイルに保存する関数
        self.df = pd.DataFrame([[sv.get() for sv in row] for row in self.sv_list])
        # 全角空白と半角空白を空文字列に変換する
        self.df = self.df.replace(r'^\s*$', "", regex=True)
        self.df = self.df.drop(self.df.index[(self.df == "").all(axis=1)])        
        self.df.to_csv(self.filepath, header = 0, index=False, encoding="shift-jis")
        self.destroy()

    def ask_save(self):
        # ウィンドウを閉じる前に保存するかどうかを尋ねる関数
        answer = mb.askyesnocancel("Save", "保存して終了しますか？")
        if   answer == True:
            self.save()
        elif answer == False:
            self.destroy()
        else:
            pass
        

root = tk.Tk()
app = App(master=root)
app.mainloop()