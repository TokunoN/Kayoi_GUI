# shファイルの行末をLFに変換する

import os
from get_filepath import get_filepath

def convert_line_endings_to_lf(filepath):
    with open(filepath, 'rb') as f:
        content = f.read()
    content = content.replace(b'\r\n', b'\n').replace(b'\r', b'\n')
    with open(filepath, 'wb') as f:
        f.write(content)

folder_path = '../sh'
folder_path = get_filepath(folder_path)

for dirpath, dirnames, filenames in os.walk(folder_path):
    for filename in filenames:
        if filename.endswith('.sh'):
            filepath = os.path.join(dirpath, filename)
            convert_line_endings_to_lf(filepath)
