# データ受信用のラズパイであるかどうかを、ユーザー名で判断する
# そのため、運用するラズパイのユーザー名は独立である必要があることを留意する。

import getpass
from get_filepath import get_filepath

def recieve_username_auth():
    this_username = getpass.getuser()
    file = "../resource/receive_username.txt"
    filepath = get_filepath(file)

    try:
        with open(filepath, encoding="shift-jis", mode = "r") as f:
            receive_username = f.read()
    # ファイルが存在しない = 受信するラズパイではない
    except FileNotFoundError as e:
        print(e)
        print("受信用ラズパイを識別するファイルが存在しません")
        return False

    if this_username != receive_username:
        print("このラズパイは受信用のラズパイではありません")
        return False
    else:
        return True