import json
import os
import math

from pyscipopt import Model
import time
from mojule.shift_scheduler import ShiftScheduler

class ShiftScheduler8(ShiftScheduler):
    def solve(self):
        u_values = {l: {s: 0 for s in range(self.n_S)} for l in range(self.n_L)}
        v_values = {l: {s: 0 for s in range(self.n_S)} for l in range(self.n_L)}

        # JSONファイル名の設定
        u_values_file = "u_values_3.json"

        ################# 1段目 #################
        if not os.path.exists(u_values_file):
            # 1段階目の計算を行う場合
            print("1段階目の計算を開始します...")

            # 目的関数: 勤務希望時間帯の多いシフトパターンから割り付け
            a = math.ceil(self.n_S * (1 / 3))
            omega_1 = 1/self.n_S*self.n_T*self.n_L
            omega_2 = self.n_S*self.n_T*self.n_L
            phi_1 = 1
            phi_2 = 1

            for l in range(self.n_L):
                model = Model(f"assign_u_l_{l}")
                u = {}
                for s in range(self.n_S):
                    u[s] = model.addVar(vtype="B", name=f"u_{l}_{s}")
                
                # a個のシフトパターンを割り付ける
                model.addCons(sum(u[s] for s in range(self.n_S)) == a)
                model.setObjective(
                    omega_1 * phi_1 * sum((self.w[s][t] * u[s] * self.h_P[l][t]) for s in range(self.n_S) for t in range(self.n_T))
                    - omega_2 * phi_2 * sum((self.w[s][t] * u[s] * self.h_N[l][t]) for s in range(self.n_S) for t in range(self.n_T)),
                    "maximize"
                )
                start = time.perf_counter()
                model.optimize()
                end = time.perf_counter()
                self.ret[7] += (end - start) * 1000
                if model.getStatus() == "optimal":
                    for s in range(self.n_S):
                        u_values[l][s] = model.getVal(u[s])
                    self.ret[0] = 1
                else:
                    print("Problem1 could not be solved to optimality")
                    for s in range(self.n_S):
                        u_values[l][s] = 0
                    self.ret[0] = 0

            # 1段階目の結果をJSONファイルに保存
            with open(u_values_file, "w") as f:
                json.dump(u_values, f, indent=4)
                print(f"1段階目の結果を保存しました: {u_values_file}")
        else:
            # JSONファイルが既に存在する場合
            print(f"{u_values_file} が既に存在するため、1段階目をスキップします。")
            self.ret[0]=1

        ################# 2段目 #################
        # 1段階目の結果をJSONファイルから読み込む
        try:
            with open(u_values_file, "r") as f:
                u_values = json.load(f)
                u_values = {int(k): {int(ks): v for ks, v in v_dict.items()} for k, v_dict in u_values.items()}
                print(f"1段階目の結果を読み込みました: {u_values_file}")
        except FileNotFoundError:
            print(f"Error: {u_values_file} が見つかりません。")
            return
        
        # 目的関数: 勤務希望を満たしつつ超過人数を最小化
        model = Model("2nd")
        v = {}
        omega = 10000

        for l in range(self.n_L):
            v[l] = {}
            for s in range(self.n_S):
                if u_values[l][s] == 1:
                    v[l][s] = model.addVar(vtype="B", name=f"v_{l}_{s}")
        
        # 不足人数が出てはならない
        for t in range(self.n_T):
            model.addCons(
                sum(v[l][s] * self.w[s][t] for l in range(self.n_L) for s in range(self.n_S) if u_values[l][s] == 1) - self.n_D[t] >= 0
            )
        

        
        # 勤務するシフトパターンは1つ以下でなければならない
        for l in range(self.n_L):
            model.addCons(
                sum(v[l][s] for s in range(self.n_S) if u_values[l][s] == 1) <= 1
            )
        
        # 目的関数の設定
        model.setObjective(
            sum(sum(self.w[s][t] * v[l][s] for s in range(self.n_S) for l in range(self.n_L) if u_values[l][s] == 1) - self.n_D[t] for t in range(self.n_T)
            ),
            "minimize"
        )

        # 最適化実行
        start_2 = time.perf_counter()
        model.optimize()
        end_2 = time.perf_counter()
        print('計測時間{:.2f}'.format((end_2 - start_2) * 1000))
        self.ret[8] = (end_2 - start_2) * 1000

        if model.getStatus() == "optimal":
            self.ret[1] = 1
            for l in range(self.n_L):
                for s in range(self.n_S):
                    if u_values[l][s] == 1:
                        v_values[l][s] = model.getVal(v[l][s])
                    else:
                        v_values[l][s] == 0

                    
            
            assigned_shifts = [100] * self.n_L
            for l in range(self.n_L):
                for s in range(self.n_S):
                    if v_values[l][s] == 1:
                        assigned_shifts[l] = s
            
            print(f"2段階目の従業員の割り当て: {assigned_shifts}")
            
            labor_positive_sum = sum(
                (self.w[s][t] * v_values[l][s] * self.h_P[l][t])
                for l in range(self.n_L)
                for s in range(self.n_S)
                for t in range(self.n_T)
            )
            self.ret[3] = labor_positive_sum / self.n_L
            print("従業員満足度:", labor_positive_sum)
            self.ret[6] = sum(
                (self.w[s][t] * v_values[l][s] * self.h_N[l][t])
                for l in range(self.n_L)
                for s in range(self.n_S)
                for t in range(self.n_T)
            )
            print("勤務不可での勤務:", self.ret[6])
        else:
            print("Problem2 could not be solved to optimality")
            self.ret[1] = 0

        # 超過人数の代入
        self.ret[2] = sum(
            sum(self.w[s][t] * v_values[l][s] for s in range(self.n_S) for l in range(self.n_L)) - self.n_D[t] for t in range(self.n_T)
        )
