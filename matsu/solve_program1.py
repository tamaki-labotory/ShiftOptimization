"""
pyscipopt
必要人数優先
第一段階:シフトパターン毎の必要人数を決定(超過人数の最小化)
第二段階:シフトパターンに従業員を割り付け(勤務希望最大化)
"""
import sys
import time

# passの設定 (pip showで出てきた、LocationのPASSを以下に設定)
sys.path.append('/Users/hymac/mypy/lib/python3.12/site-packages')
import json
import math
import numpy as np
from pyscipopt import Model

def solve(file_path,printLog):

    # JSONファイルからデータを読み込む
    with open(file_path, "r") as f:
        shift_data = json.load(f)

    

    # 定数の設定
    n_S = np.array(shift_data["shift_patterns"]).shape[0]
    n_T = np.array(shift_data["shift_patterns"]).shape[1]
    n_L = np.array(shift_data["preferences"]).shape[0]

    # 時間帯当たり必要人数
    n_D = shift_data["required_employees"]

    # 各シフトパターンごとで、勤務する時間帯でか（1: 必要、0: 不要）
    w = shift_data["shift_patterns"]

    # 従業員の勤務希望（1: 希望、0: 不希望）
    h_P = shift_data["preferences"]

    # 従業員の勤務不可能（1: 不可、0: ？）
    h_N = shift_data["unavailable_slots"]

    #初期化
    x_values = {s:0 for s in range(n_S)}
    y_values = {l: {s : 0 for s in range(n_S)}for l in range(n_L)}
    #返り値
    #[1段階目成功可否,2段階目成功可否,超過人数評価指標,希望充足評価指標,時間評価指標]
    ret=[0]*5

    model = Model("1st")
    x = {}
    for s in range(n_S):
        x[s] = model.addVar(f"x_{s}",vtype = "I")
    for t in range(n_T):
        model.addCons(
            sum(w[s][t] * x[s] for s in range(n_S)) >= n_D[t]
        )
    model.addCons(x[s] >= 0)
    model.setObjective(
        sum(sum(w[s][t] * x[s] for s in range(n_S))-n_D[t] for t in range(n_T)),"minimize"
    )

    model.optimize()
    if model.getStatus() == "optimal":
        for s in range(n_S):
            x_values[s] = model.getVal(x[s])
        ret[0] = 1
        over_labors = model.getObjVal() 
        ret[2] = over_labors/sum(n_D[t] for t in range(n_T))
        if printLog:
            print(f"超過人数：{over_labors}")
            print(f"各シフトパターンの割り付け人数：{x_values}")
    else:
        print("Problem1 could not be solved to optimality")
        ret[0] = 0
    

    # #################２段目#################
    start = time.perf_counter()
    model = Model("2nd")

    y = {}
    for l in range(n_L):
        y[l] = {}
        for s in range(n_S):
            y[l][s] = model.addVar(vtype="B", name=f"y_{l}_{s}")
    
    model.addCons(
            sum(w[s][t] * y[l][s] * h_N[l][t] for s in range(n_S) for t in range(n_T) for l in range(n_L)) == 0
        )
    
    for s in range(n_S):
        model.addCons(
            sum(y[l][s] for l in range(n_L)) == x_values[s]
        )
    
    for l in range(n_L):
        model.addCons(
            sum(y[l][s] for s in range(n_S)) <= 1
        )
    
    model.setObjective(
        sum(w[s][t] * y[l][s] * h_P[l][t] for s in range(n_S) for t in range(n_T) for l in range(n_L)),"maximize"
    )
    model.optimize()
    end = time.perf_counter()
    if model.getStatus() == "optimal":
        ret[1] = 1
        for l in range(n_L):
            for s in range(n_S):
                y_values[l][s] = model.getVal(y[l][s])
        assigned_shifts = [100] * n_L
        for l in range(n_L):
            for s in range(n_S):
                if y_values[l][s] == 1:
                    assigned_shifts[l] = s
        print(f"２階目の従業員の割り当て:{assigned_shifts}")
        labor_positive_sum = sum((w[s][t] * y_values[l][s] * h_P[l][t]) 
                                 for l in range(n_L) for s in range(n_S) for t in range(n_T))
        want_work = sum(h_P[l][t] for l in range(n_L) for t in range(n_T))/(n_L*n_T)
        ret[3] = labor_positive_sum /(sum(w[s][t] * y_values[l][s] for s in range(n_S) for t in range(n_T) for l in range(n_L)) * want_work)
        print("従業員満足度:",labor_positive_sum)
        
    else:
        print("Problem2 could not be solved to optimality")
        ret[1] = 0

    print('計測時間{:.2f}'.format((end-start)*1000)) 
    ret[4] = (end-start)*1000
    return ret