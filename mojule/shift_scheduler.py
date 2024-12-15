##帆前環境用
import sys
sys.path.append('/Users/hymac/mypy/lib/python3.12/site-packages')
##
import json
import numpy as np
from pulp import LpProblem, LpVariable, LpMinimize, LpMaximize, lpSum, PULP_CBC_CMD, value

class ShiftScheduler:
    def __init__(self, file_paths, print_log=False):
        self.file_paths = file_paths
        self.print_log = print_log
        self.shift_data = self._load_data() #データをロード

        #シフトパターン数
        self.n_S = len(self.shift_data["shift_patterns"]) 

        #時間帯数
        self.n_T = len(self.shift_data["shift_patterns"][0])

         #従業員数
        self.n_L = len(self.shift_data["preferences"])

        # 時間帯当たり必要人数
        self.n_D = self.shift_data["required_employees"]

        # 各シフトパターンごとで、勤務する時間帯でか（1: 必要、0: 不要）
        self.w = self.shift_data["shift_patterns"]

        # 従業員の勤務希望（1: 希望、0: 不希望）
        self.h_P = self.shift_data["preferences"]

        # 従業員の勤務不可能（1: 不可、0: 不明）
        self.h_N = self.shift_data["unavailable_slots"]

        #返り値
        #[1段階目成功可否,2段階目成功可否,超過人時,希望充足時,???,???]
        self.ret=[0]*6

    def _load_data(self):
            """データを3つのJSONファイルからロード"""
            data = {}

            # シフトパターン
            with open(self.file_paths["shift_patterns"], "r") as f:
                data["shift_patterns"] = json.load(f)["shift_patterns"]

            # 勤務希望と勤務不可能
            with open(self.file_paths["preferences_and_unavailable_slots"], "r") as f:
                pref_data = json.load(f)
                data["preferences"] = pref_data["preferences"]
                data["unavailable_slots"] = pref_data["unavailable_slots"]

            # 時間帯当たり必要人数
            with open(self.file_paths["required_employees"], "r") as f:
                data["required_employees"] = json.load(f)["required_employees"]

            return data
        
    '''
    #データをロードする関数
    def _load_data(self):
        with open(self.file_path, "r") as f:
            return json.load(f)
    '''
    #問題を解く関数
    def solve(self):
        raise NotImplementedError("Subclasses should implement the solve method.")

    #結果を出力する関数
    def print_results(self):
        if self.print_log:
            print(f"Step 1 Status: {'Success' if self.ret[0] == 1 else 'Failure'}")
            print(f"Step 2 Status: {'Success' if self.ret[1] == 1 else 'Failure'}")
            print(f"Overstaffing Hours: {self.ret[2]}")
            print(f"Employee Satisfaction: {self.ret[3]}")