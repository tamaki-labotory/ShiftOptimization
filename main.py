"""
各種ソルバーを実行するメインプログラム
"""
##帆前環境用
import sys
sys.path.append('/Users/hymac/mypy/lib/python3.12/site-packages')
##
from mojule import mediator


# メインプログラムとして実行された場合にmain()を呼び出す
if __name__ == "__main__":

    #松村用実行関数
    #mediator.mediator("m","/Users/matsumura/Desktop/修論/program/json/shift_data132.json",True)
    #帆前用実行関数
    file_paths = {
        "shift_patterns": "/Users/hymac/mypy/ShiftOptimization-progress1/json/shift_patterns_1.json",
        "preferences_and_unavailable_slots": "/Users/hymac/mypy/ShiftOptimization-progress1/json/preferences_and_unavailable_slots_1.json",
        "required_employees": "/Users/hymac/mypy/ShiftOptimization-progress1/json/required_employees_1.json"
    }
    mediator.mediator("m",file_paths,True)