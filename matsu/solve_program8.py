'''
現状これを最適解とする.
超過人数の減少を主の目的とし,同一の超過人数のもとで勤務希望での勤務時間帯を最大化する.
一段階の最適化
'''

import sys
# passの設定 (pip showで出てきた、LocationのPASSを以下に設定)
sys.path.append('/Users/hymac/mypy/lib/python3.12/site-packages')
import json
import numpy as np
import time
from pyscipopt import Model

def solve(file_path, printLog):
    # JSONファイルからデータを読み込む
    with open(file_path, "r") as f:
        shift_data = json.load(f)

    # 定数の設定
    n_S = np.array(shift_data["shift_patterns"]).shape[0]  # シフト数
    n_T = np.array(shift_data["shift_patterns"]).shape[1]  # 時間帯数
    n_L = np.array(shift_data["preferences"]).shape[0]     # 従業員数

    # 時間帯当たり必要人数
    n_D = shift_data["required_employees"]

    # 各シフトパターンごとの勤務時間帯（1: 必要、0: 不要）
    w = shift_data["shift_patterns"]

    # 従業員の勤務希望（1: 希望、0: 不希望）
    h_P = shift_data["preferences"]

    # 従業員の勤務不可能（1: 不可、0: 可能）
    h_N = shift_data["unavailable_slots"]

    # 目的関数の係数
    omega_1 = 1   # 希望充足度
    omega_2 = -1  # 超過人数ペナルティ
    u_values = {l: {s : 0 for s in range(n_S)}for l in range(n_L)}
    ret=[0]*5


    start = time.perf_counter()
    # モデルの設定
    model = Model("Shift_Optimization")

    # 変数の定義
    u = {}
    for l in range(n_L):
        u[l] = {}
        for s in range(n_S):
            u[l][s] = model.addVar(vtype="B", name=f"u_{l}_{s}")
    
    # 各従業員の制約
    for l in range(n_L):
        # 各従業員は1つのシフトにしか割り当てられない
        model.addCons(sum(u[l][s] for s in range(n_S)) <= 1)
        
        # 不可能な勤務時間帯を避ける
        model.addCons(
            sum(w[s][t] * u[l][s] * h_N[l][t] for s in range(n_S) for t in range(n_T)) == 0
        )

    
    for t in range(n_T):
        model.addCons(
            sum(w[s][t] * u[l][s] for s in range(n_S) for l in range(n_L)) >= n_D[t]
            )


    # 目的関数の設定（勤務希望充足度の最大化と、超過人数のペナルティ最小化）
    model.setObjective(
        sum(sum(w[s][t] * u[l][s] for s in range(n_S) for l in range(n_L)) - n_D[t] for t in range(n_T))-
        0.0001 * sum(w[s][t] * u[l][s] * h_P[l][t] for l in range(n_L) for t in range(n_T) for s in range(n_S)),
        "minimize"
    )

    # 最適化の実行
    model.optimize()
    end = time.perf_counter()

    # 最適化結果の出力
    if model.getStatus() == "optimal":
        print("Optimal Solution Found!")
        ret[0]=1
        ret[1]=1
        
        for l in range(n_L):
            for s in range(n_S):
                u_values[l][s] = model.getVal(u[l][s])
        # 超過人数の出力
        over_labors = sum(sum(w[s][t] * u_values[l][s] for s in range(n_S) for l in range(n_L)) - n_D[t] for t in range(n_T))
        print(f"超過人数：{over_labors}")
        
        ret[2] = over_labors/sum(n_D[t] for t in range(n_T))
        


        # 希望充足度の合計を計算
        labor_positive_sum = sum((w[s][t] * u_values[l][s] * h_P[l][t]) 
                                 for l in range(n_L) for s in range(n_S) for t in range(n_T))
        print("従業員満足度:",labor_positive_sum)
        want_work = sum(h_P[l][t] for l in range(n_L) for t in range(n_T))/(n_L*n_T)
        ret[3] = labor_positive_sum /(sum(w[s][t] * u_values[l][s] for s in range(n_S) for t in range(n_T) for l in range(n_L)) * want_work)
        
        # 各従業員の割り当てシフトパターンの出力
        print("\nShift Assignments:")
        for p in range(n_L):
            assigned_shifts = [s for s in range(n_S) if model.getVal(u[p][s]) == 1]
            if assigned_shifts:
                print(f"Employee {p}: Assigned Shift = {assigned_shifts}")
            else:
                print(f"Employee {p}: No Shift Assigned")
        
    else:
        print("Problem could not be solved to optimality")
    print('計測時間{:.2f}'.format((end-start)*1000)) 
    ret[4] = (end-start)*1000
    return ret

# ファイルパスの指定と呼び出し例
# solve("/path/to/shift_data.json", printLog=True)
