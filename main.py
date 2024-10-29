"""
各種ソルバーを実行するメインプログラム
"""
from matsu import mediator


# メインプログラムとして実行された場合にmain()を呼び出す
if __name__ == "__main__":

    #松村用実行関数
    mediator.mediator("m","./json/shift_data85.json",False)