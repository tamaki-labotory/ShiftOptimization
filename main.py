"""
各種ソルバーを実行するメインプログラム
"""
from mojule import mediator


# メインプログラムとして実行された場合にmain()を呼び出す
if __name__ == "__main__":

    #松村用実行関数
    mediator.mediator("m","/Users/matsumura/Desktop/修論/program/json/shift_data132.json",True)