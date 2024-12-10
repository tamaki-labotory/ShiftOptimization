"""
各種ソルバーを実行するメインプログラム
"""
import sys

# passの設定 (pip showで出てきた、LocationのPASSを以下に設定)
sys.path.append('/Users/hymac/mypy/lib/python3.12/site-packages')
from matsu import mediator


# メインプログラムとして実行された場合にmain()を呼び出す
if __name__ == "__main__":
    #松村用実行関数
    mediator.mediator("n","./json/base_data.json",True)