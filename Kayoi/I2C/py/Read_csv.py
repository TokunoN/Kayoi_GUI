# pd.read_csvを定型的に使う場合に入力を簡素化する

import pandas as pd

class Read_csv():
    def __init__(self, file, **kwargs):
        self.file = file
        try:
            self.index_col = kwargs["index_col"]
        except KeyError:
            self.index_col = False

    def __enter__(self):
        return pd.read_csv(self.file, encoding="shift-jis", index_col = self.index_col)
    def __exit__(self, exception_type, exception_value, traceback):
        exception_list = [exception_type, exception_value, traceback]
        for exception in exception_list:
            if exception != None:
                print(exception)
        pass

# 使用テンプレ
# from Read_csv import Read_csv
#with Read_csv(filepath) as df:
#    output_df = df