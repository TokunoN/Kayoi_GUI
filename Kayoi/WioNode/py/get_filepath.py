# 絶対パスを使用するときの、ラズパイ(Linux)とWindowsでのディレクトリの違いを吸収する。
# このコードを利用するファイルと同じディレクトリに配置して使用すること
# 使用例: 
# from get_filepath import get_filepath
# file = "../resource/hogehoge.csv"
# filepath = get_filepath(file)

import os

def get_filepath(file):    
    return os.path.normpath(os.path.join(
            os.path.abspath(os.path.dirname(__file__)), file))