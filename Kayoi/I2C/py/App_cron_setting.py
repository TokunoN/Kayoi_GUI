# cronの設定をするGUIアプリケーション

import flet as ft
import pandas as pd
from get_filepath import get_filepath
import os

class CronSetRaw(ft.Row):
    def __init__(self):
        super().__init__()

        self.__cb_value = True
        self.__dd_value = 5
        self.__title_text = "text"

        self.cb = ft.Checkbox(value = self.__cb_value, on_change=self.checkbox_changed)
        
        self.tt = ft.Text(self.__title_text, width=title_text_width)
        colon = ft.Text(" : ")
        
        # 通知間隔の設定リスト
        # cronをうまく動かすためには60の約数か倍数であることが望ましい
        # それらでなくともよいが、厳密にn分ごとに動かすためには工夫が必要と思われる
        option_list = [5, 10, 15, 20, 30, 60, 120]
        dd_option_list = [ft.dropdown.Option(option) for option in option_list]
        self.dd = ft.Dropdown(
            width = dd_and_tf_width,
            options=dd_option_list,
            value=self.__dd_value,
            suffix=ft.Text("分毎に実行"),
            on_change= self.dropdown_changed
        )
        # 余力があれば: 
        # データ取得より警報通知や定期通知の周期が短い場合、同じ通知が複数回届くことになるので、
        # そのあたりの警告を出せるとよい。

        self.disabled_message_text = ft.Text("実行しません", visible=False, width=dd_and_tf_width)
        
        # チェックボックス、テキスト、コロン、ドロップダウンリスト、実行しないことを示すテキスト、の順番
        self.controls = [
            self.cb,
            self.tt,
            colon,
            self.dd,
            self.disabled_message_text
        ]
        self.alignment = "center"
        self.vertical_alignment = "center"
        self.height = 75

    def checkbox_changed(self, e):
        # チェックボックスがオフのときに「実行されない」テキストを表示
        is_checked = True if e.data == "true" else False
        self.__cb_value = is_checked
        self.dd.visible = is_checked
        self.disabled_message_text.visible = not is_checked
        self.page.update()

    def dropdown_changed(self, e):
        self.__dd_value = self.dd.value
        self.page.update()

    @property
    def cb_value(self):
        return self.__cb_value
    
    @cb_value.setter
    def cb_value(self, value):
        self.__cb_value = value
        self.cb.value = self.__cb_value
        self.page.update()
        
    @property
    def dd_value(self):
        return self.__dd_value
    
    @dd_value.setter
    def dd_value(self, value):
        self.__dd_value = value
        self.dd.value = self.__dd_value 
        self.page.update()
        
    @property
    def title_text(self):
        return self.__title_text
    
    @title_text.setter
    def title_text(self, value):
        self.__title_text = value
        self.tt.value = self.__title_text
        self.page.update()

def main(page: ft.Page):
    # 日本語フォントの設定
    font_file = "assets/fonts/NotoSansJP-Light.otf"
    font_filepath = get_filepath(font_file)
    if os.path.exists(font_filepath) == False:
        message = "日本語表示用のフォントファイルが存在しません"
        file = "../stderr.log"
        filepath = get_filepath(file)
        with open(filepath, mode = "a") as f:
            f.write(message + "\n")
        return
    page.fonts = {
            "NotoSansJP": font_filepath
    }

    # page.theme はライトモードのテーマ
    # page.dark_theme はダークモードのテーマ
    # https://github.com/flet-dev/flet/issues/544
    # どちらが選択されるか分からないので両方記述しておく。
    page.theme = ft.Theme(font_family="NotoSansJP")
    page.dark_theme = ft.Theme(font_family="NotoSansJP")

    def window_event(e):
        # ウィンドウを閉じたときにダイアログを表示
        if e.data == "close":
            page.dialog = close_confirm_dialog
            close_confirm_dialog.open = True
            page.update()

    def save_yes_click(e):
        # 保存するときの処理
        # cronはcsvに、日報作成可否とユーザ名はtxtに保存
        for i, row in enumerate(e.page.controls):
            if i < len(cronsetrow_list):
                df.iloc[i, :] = [row.cb_value, row.dd_value]
            elif i == len(cronsetrow_list):
                daily_report_run_flag = row.controls[0].value
            else:
                receive_username = row.controls[3].value

        df.to_csv(df_filepath, header=True, index=True, encoding = "shift-jis")
        with open(daily_report_run_flag_filepath, encoding="shift-jis", mode = "w") as f:
            f.write(str(daily_report_run_flag))
        with open(receive_username_filepath, encoding="shift-jis", mode = "w") as f:
            f.write(receive_username)

        close_confirm_dialog.open = False
        page.dialog = after_save_dialog
        after_save_dialog.open = True
        page.update()
        # page.window_destroy()

    def save_no_click(e):
        page.window_destroy()

    def close_no_click(e):
        close_confirm_dialog.open = False
        page.update()

    # def cb_changed(e):
    #     e.value = not e.value
    #     page.update()

    
    page.window_prevent_close = True
    page.on_window_event = window_event

    close_confirm_dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("アプリを終了します"),
        content=ft.Text("保存していない変更を保存しますか？"),
        actions=[
            ft.ElevatedButton("終了しない", on_click=close_no_click),
            ft.ElevatedButton("変更を破棄して終了", on_click=save_no_click),
            ft.OutlinedButton("変更を保存して終了", on_click=save_yes_click),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )

    # 保存後の注意書き
    # あくまで設定を書き出しているだけでcronに設定を入力しているわけではない。
    after_save_dialog = ft.AlertDialog(
        modal = True,
        title = ft.Text("変更を保存しました"),
        content = ft.Text("この後、ラズパイ上でcron設定プログラムを実行してください"),
        actions=[
            ft.OutlinedButton("了解", on_click= save_no_click)
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )

    global df
    # global df_filepath
    file = "../resource/cron_setting.csv"
    df_filepath = get_filepath(file)
    if os.path.exists(df_filepath):
        df = pd.read_csv(df_filepath, header=0, index_col=0, encoding="shift-jis")
    else:
        df = pd.DataFrame(
            [[True, 5] for i in range(4)],
            columns=["run_flag", "run_span"],
            index = ["data_getting", "notify_period", "notify_alert", "data_receiving"])

    file = "../resource/daily_report_run_flag.txt"
    daily_report_run_flag_filepath = get_filepath(file)
    try:
        with open(daily_report_run_flag_filepath, encoding="shift-jis", mode = "r") as f:
            daily_report_run_flag = True if f.read() == "True" else False
    # 初期設定としてはTrue
    except FileNotFoundError:
        daily_report_run_flag = True

    file = "../resource/receive_username.txt"
    receive_username_filepath = get_filepath(file)
    try:
        with open(receive_username_filepath, encoding="shift-jis", mode = "r") as f:
            receive_username = f.read()
    except FileNotFoundError:
        receive_username = ""


    global title_text_width
    global dd_and_tf_width
    title_text_width = 250
    dd_and_tf_width = 150

    data_getting = CronSetRaw()
    notify_alert = CronSetRaw()
    notify_period = CronSetRaw()
    data_receiving = CronSetRaw()

    title_text_list = [
        "センサーからデータを取得する間隔",
        "警報を通知する間隔",
        "定期的にデータを通知する間隔",
        "Ambientからデータを取得する間隔",
        "日報作成の可否",
        "Ambientからデータを取得する"+"\n"+"ラズパイのユーザー名"
        ]
    cronsetrow_list = [data_getting, notify_alert, notify_period, data_receiving]


    daily_report_cb = ft.Row(controls=[
        ft.Checkbox(value=daily_report_run_flag),
        ft.Text(title_text_list[4], width = title_text_width),
        ft.Text("   "), # 見た目調整用
        ft.Text(width = dd_and_tf_width) # 見た目調整用
    ],
    alignment = "center",
    vertical_alignment = "center",
    height = 75
    )
    
    receive_username_tf =  ft.Row(controls=[
        ft.Text(width = 40),
        ft.Text(title_text_list[5], width=title_text_width),
        ft.Text(" : "),
        ft.TextField(value=receive_username, width=dd_and_tf_width),
        
    ],
    alignment = "center",
    vertical_alignment = "center",
    height = 75
    )
    # receive_username_tf = ft.TextField(value=receive_username)
    
    page.add(
        data_getting,
        notify_alert,
        notify_period,
        data_receiving,
        daily_report_cb,
        receive_username_tf
    )
    for i, row in enumerate(cronsetrow_list):
        row.cb_value = bool(df.iloc[i, 0])
        row.title_text = title_text_list[i]
        row.dd_value = df.iloc[i, 1]
        row.controls[3].visible = bool(df.iloc[i, 0])
        row.controls[4].visible = not bool(df.iloc[i, 0])
        
    page.update()


ft.app(target=main, assets_dir="assets")