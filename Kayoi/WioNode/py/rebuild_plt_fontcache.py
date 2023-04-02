# matplotlib.pyplotで日本語フォントを使用したグラフを描画する
# フォントのキャッシュを消去した後で使用することで、日本語フォントを含めた状態でキャッシュを再構成する
import matplotlib.font_manager as fm
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

font_path = "/usr/share/fonts/opentype/noto/NotoSansJP/NotoSansJP-Light.otf"
font_prop = fm.FontProperties(fname=font_path)
plt.rcParams["font.family"] = font_prop.get_name()

sns.set()
sns.set_theme(style = "whitegrid", font = font_prop.get_name(), font_scale=1.5)
 
# 二次曲線の作成
x = np.linspace(-3,3)
y = x**2
  
# 二次曲線のプロット作成
plt.plot(x, y, label="二次曲線")
 
# タイトル・軸ラベル表示
plt.title("グラフタイトル")
plt.xlabel("x軸ラベル名")
plt.ylabel("y軸ラベル名")
 
# グラフ内テキスト表示
plt.text(0, 4,"テキスト例")
 
# 凡例表示
plt.legend()
 
plt.show()