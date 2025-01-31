import json
import os
from pyscipopt import Model
import time
from mojule.shift_scheduler import ShiftScheduler

class ShiftScheduler5(ShiftScheduler):
    def solve(self):
        x_values = {s: 0 for s in range(self.n_S)}
        y_values = {l: {s: 0 for s in range(self.n_S)} for l in range(self.n_L)}

        # JSONファイル名の設定
        x_values_file = "x_values.json"

        ################# 1段目 #################
        if not os.path.exists(x_values_file):
            # 1段階目の計算を行う場合
            print("1段階目の計算を開始します...")
            
            # 目的関数: 超過人数の最小化
            model = Model("1st")
            x = {}
            for s in range(self.n_S):
                x[s] = model.addVar(f"x_{s}", vtype="I")
            
            # 必要人数を満たす制約
            for t in range(self.n_T):
                model.addCons(sum(self.w[s][t] * x[s] for s in range(self.n_S)) >= self.n_D[t])
            
            # 変数の非負制約
            for s in range(self.n_S):
                model.addCons(x[s] >= 0)
            
            # 目的関数の設定
            model.setObjective(
                sum(sum(self.w[s][t] * x[s] for s in range(self.n_S)) - self.n_D[t] for t in range(self.n_T)
                ),
                "minimize"
            )

            # 最適化実行
            start = time.perf_counter()
            model.optimize()
            end = time.perf_counter()
            self.ret[7] = (end - start) * 1000

            # 最適解の確認と保存
            if model.getStatus() == "optimal":
                for s in range(self.n_S):
                    x_values[s] = model.getVal(x[s])
                self.ret[0] = 1
                if self.print_log:
                    print(f"各シフトパターンの割り付け人数：{x_values}")
                
                # 1段階目の結果をJSONファイルに保存
                with open(x_values_file, "w") as f:
                    json.dump(x_values, f, indent=4)
                    print(f"1段階目の結果を保存しました: {x_values_file}")
            else:
                print("Problem1 could not be solved to optimality")
                self.ret[0] = 0
                return  # 1段階目が失敗した場合、処理を終了する
        else:
            # JSONファイルが既に存在する場合
            print(f"{x_values_file} が既に存在するため、1段階目をスキップします。")
            self.ret[0] = 1

        ################# 2段目 #################
        # 1段階目の結果をJSONファイルから読み込む
        try:
            with open(x_values_file, "r") as f:
                x_values = json.load(f)
                x_values = {int(k): v for k, v in x_values.items()}
                print(f"1段階目の結果を読み込みました: {x_values}")
        except FileNotFoundError:
            print(f"Error: {x_values_file} が見つかりません。")
            return
        
        # 目的関数: 勤務希望の最大化
        model = Model("2nd")
        y = {}
        omega_1 = 1 / (self.n_S * self.n_T * self.n_L)
        omega_2 = 1

        # 従業員割り付け変数
        for l in range(self.n_L):
            y[l] = {}
            for s in range(self.n_S):
                y[l][s] = model.addVar(vtype="B", name=f"y_{l}_{s}")

        # 制約1: シフトごとの必要人数を満たす
        for s in range(self.n_S):
            model.addCons(
                sum(y[l][s] for l in range(self.n_L)) == x_values[s]
            )

        # 制約2: 従業員は1つのシフトパターンにのみ割り当てられる
        for l in range(self.n_L):
            model.addCons(
                sum(y[l][s] for s in range(self.n_S)) <= 1
            )

        # 目的関数の設定
        model.setObjective(
            sum(
                omega_1 * self.w[s][t] * y[l][s] * self.h_P[l][t]
                - omega_2 * self.w[s][t] * y[l][s] * self.h_N[l][t]
                for s in range(self.n_S)
                for t in range(self.n_T)
                for l in range(self.n_L)
            ),
            "maximize"
        )

        # 最適化実行
        start = time.perf_counter()
        model.optimize()
        end = time.perf_counter()

        # 結果の記録

        self.ret[8] = (end - start) * 1000
        if model.getStatus() == "optimal":
            self.ret[1] = 1
            for l in range(self.n_L):
                for s in range(self.n_S):
                    y_values[l][s] = model.getVal(y[l][s])
            ##超過人数の代入
            self.ret[2] =  sum(sum(self.w[s][t]*y_values[l][s] for l in range(self.n_L) for s in range(self.n_S))- self.n_D[t] for t in range(self.n_T))
            labor_positive_sum = sum(
                (self.w[s][t] * y_values[l][s] * self.h_P[l][t])
                for l in range(self.n_L)
                for s in range(self.n_S)
                for t in range(self.n_T)
            )
            self.ret[3] = labor_positive_sum / self.n_L
            self.ret[6] = sum(
                (self.w[s][t] * y_values[l][s] * self.h_N[l][t])
                for l in range(self.n_L)
                for s in range(self.n_S)
                for t in range(self.n_T)
            )
        else:
            print("Problem2 could not be solved to optimality")
            self.ret[1] = 0

        print('計測時間{:.2f}'.format((end - start) * 1000))
