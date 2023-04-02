# LINE notifyへの通知用の設定を行うGUIアプリケーション
# WioNode関連の設定も行う。

import flet as ft
import pandas as pd
from Read_csv import Read_csv
from get_filepath import get_filepath
import math
import os

class Table(ft.UserControl):
    def __init__(self):
        super().__init__()
        self.path = os.path.dirname(__file__)
        self.file = ""

    def select_changed(self, e):
        e.control.selected = not e.control.selected
        self.update()

    def delete_selected_row(self, e):
        delete_row_list = []
        for row in self.dt.rows:
            if row.selected == True:
                delete_row_list.append(row)
        for row in delete_row_list:
            self.dt.rows.remove(row)
        self.update()
    
    def add_row(self, e):
        add_datarow = ft.DataRow(on_select_changed=self.select_changed)
        for i in self.textfield_row.controls:
            add_datarow.cells.append(ft.DataCell(ft.Text(i.value), show_edit_icon=False))
            i.value = ""
        self.dt.rows.append(add_datarow)
        self.update()

    def save_dt_to_csv(self, e):
        df_for_csv = pd.DataFrame(
            data = [[cell.content.value  for cell in row.cells] for row in self.dt.rows],
            columns = [col.label.value for col in self.dt.columns]
        )
        df_for_csv.to_csv(get_filepath(self.file), encoding="shift-jis", index = False)

    def build(self):
        self.dt = ft.DataTable(show_checkbox_column=True)
        self.dt.columns = (list(map(lambda x: ft.DataColumn(ft.Text(x)), self.df.columns)))
        for index in self.df.index:
            dc = list(map(lambda x: ft.DataCell(ft.Text(x if (isinstance(x, str)) or (math.isnan(x) == False) else ""), show_edit_icon=False), self.df.loc[index,:]))
            dr = ft.DataRow(cells=dc, selected=False)
            dr.on_select_changed = self.select_changed
            self.dt.rows.append(dr)

        self.textfield_row = ft.Row([ft.TextField(
            label = col,
            width = window_width / len(self.df.columns) * 0.92
            ) for col in self.df.columns])

        self.delete_btn = ft.ElevatedButton(text="削除", on_click=self.delete_selected_row)
        self.add_btn = ft.ElevatedButton(text="追加", on_click=self.add_row)
        self.save_btn = ft.ElevatedButton(text="保存", on_click=self.save_dt_to_csv)

        self.return_col = ft.Column([
            ft.Row([self.dt], scroll="adaptive"), 
            self.textfield_row,
            ft.Row([self.delete_btn, self.add_btn, self.save_btn])
        ], horizontal_alignment="center", scroll="adaptive")

        return self.return_col



class LINE_Token_Table(Table):
    def __init__(self):
        super().__init__()
        self.file = "../resource/line_token.csv"

        try:
            with Read_csv(get_filepath(self.file)) as d:
                self.df = d
        except FileNotFoundError:
            self.df = pd.DataFrame(columns=["アクセストークン", "LINEのグループ名", "通知目的"])

class WioNode_Table(Table):
    def __init__(self):
        super().__init__()
        self.file = "../resource/WioNode_setting.csv"

        try:
            with Read_csv(get_filepath(self.file)) as d:
                self.df = d
        except FileNotFoundError:
            self.df = pd.DataFrame(columns=["アクセストークン", "ハウス名", "データの種類"])

class DataType_Table(Table):
    def __init__(self):
        super().__init__()
        self.file = "../resource/datatype_setting.csv"

        try:
            with Read_csv(get_filepath(self.file)) as d:
                self.df = d
        except FileNotFoundError:
            self.df = pd.DataFrame(columns=["データの種類", "単位", "下限警告文", "上限警告文", "下限閾値", "上限閾値"])

class Graph_Table(Table):
    def __init__(self):
        super().__init__()
        self.file = "../resource/graph_datatype_setting.csv"

        try:
            with Read_csv(get_filepath(self.file)) as d:
                self.df = d
        except FileNotFoundError:
            self.df = pd.DataFrame(columns=["グラフID", "データの種類1", "データの種類2", "データの種類3", "データの種類4"])



def main(page: ft.Page):
    file = "assets/fonts/NotoSansJP-Light.otf"
    filepath = get_filepath(file)
    if os.path.exists(filepath) == False:
        message = "日本語表示用のフォントファイルが存在しません"
        file = "../stderr.log"
        filepath = get_filepath(file)
        with open(filepath, mode = "a") as f:
            f.write(message + "\n")
        return
    page.fonts = {
            "NotoSansJP": filepath
    }

    # page.theme はライトモードのテーマ
    # page.dark_theme はダークモードのテーマ
    # https://github.com/flet-dev/flet/issues/544
    # どちらが選択されるか分からないので両方記述しておく。
    page.theme = ft.Theme(font_family="NotoSansJP")
    page.dark_theme = ft.Theme(font_family="NotoSansJP")

    def window_event(e):
        if e.data == "close":
            page.dialog = close_confirm_dialog
            close_confirm_dialog.open = True
            page.update()

    def save_yes_click(e):
        for tab in t.tabs:
            tab.content.save_dt_to_csv(e)
        page.window_destroy()

    def save_no_click(e):
        page.window_destroy()

    def close_no_click(e):
        close_confirm_dialog.open = False
        page.update()
    
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

    # windowのサイズをグローバル宣言
    # Table()の中からwindowのサイズを取得できる方法が見つかれば必要ない
    global window_width
    window_width = page.window_width

    t = ft.Tabs(
        selected_index=0,
        animation_duration=300,
        tabs=[
            ft.Tab(
                text="LINE",
                content=LINE_Token_Table(),
                icon=ft.icons.PHONE_IPHONE
            ),
            ft.Tab(
                text = "WioNode",
                content=WioNode_Table(),
                icon = ft.icons.DEVICE_THERMOSTAT
            ),
            ft.Tab(
                text="データの種類",
                content=DataType_Table(),
                icon = ft.icons.SETTINGS
            ),
            ft.Tab(
                text = "グラフ",
                content = Graph_Table(),
                icon  = ft.icons.SHOW_CHART
            )
        ],
        expand=1,
    )

    page.add(t)


ft.app(target=main, assets_dir="assets")