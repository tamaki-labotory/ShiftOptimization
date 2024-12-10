"""
1段階目:各シフトパターンに割り当てる人数を確定
2段階目:従業員を各シフトパターンに割り付ける
という順でシフトを作成するプログラム

勤務希望優先,一段階目で許容するシフト割り付けの数を変化
"""
import sys
import time

# passの設定 (pip showで出てきた、LocationのPASSを以下に設定)
sys.path.append('/Users/hymac/mypy/lib/python3.12/site-packages')
import json
import numpy as np
from pulp import LpProblem, LpVariable, LpMinimize,LpMaximize, lpSum, LpStatus, LpStatusOptimal,PULP_CBC_CMD, value
from pyscipopt import Model

def solve(file_path,printLog):

    # JSONファイルからデータを読み込む
    with open(file_path, "r") as f:
        shift_data = json.load(f)

    # # 読み込んだデータの表示
    # print("Required Employees per Time Slot:")
    # print(shift_data["required_employees"])

    # print("\nShift Patterns:")
    # for i, pattern in enumerate(shift_data["shift_patterns"]):
    #     print(f"Pattern {i+1}: {pattern}")

    # print("\nPreferences:")
    # for i, preference in enumerate(shift_data["preferences"]):
    #     print(f"Employee {i+1}: {preference}")

    # print("\nUnavailable Slots:")
    # for i, unavailable in enumerate(shift_data["unavailable_slots"]):
    #     print(f"Employee {i+1}: {unavailable}")

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
    

    # 初期化：v_values（各従業員の勤務フラグ）
    v_values = {p: {s: 0 for s in range(n_S)} for p in range(n_L)} # 従業員が働くかどうかのフラグ

    

    # 初期化：勤務充足度を保存する辞書
    work_satisfaction = {}

    # 初期化：u_values のデフォルト初期化（全従業員・全シフトを対象）
    u_values = {p: {s: 0 for s in range(n_S)} for p in range(n_L)}
    ret=[0]*5

    for p in range(n_L):
        model = Model(f"assign_u_p_{p}")
        u = {}
        for s in range(n_S):
            u[s] = model.addVar(f"u_{p}_{s}", vtype = "B")
        model.addCons(sum(u[s] for s in range(n_S)) <= 1)
        model.addCons(
            sum(w[s][t] * u[s] * h_N[p][t] for s in range(n_S) for t in range(n_T)) == 0
        )
        model.setObjective(
            sum(w[s][t] * u[s] * h_P[p][t] for t in range(n_T) for s in range(n_S))+0.001*sum(w[s][t]*u[s] for t in range(n_T) for s in range(n_S)),"maximize"
        )
        model.optimize()
        if model.getStatus() == "optimal":
                for s in range(n_S):
                    u_values[p][s]=model.getVal(u[s])
                #work_satisfaction[p] = model.getVal(u[s])                
        else:
                print("Problem could not be solved to optimality")
                for s in range(n_S):
                    u_values[p][s]=0
                work_satisfaction[p] = 0

                
    # ---- 第二段階: v[p]を決定しペナルティを最小化する ----
    start = time.perf_counter()
    model = Model("assign_v")

    # 変数の定義
    v = {}
    for p in range(n_L):
        v[p] = {}
        for s in range(n_S):
            v[p][s] = model.addVar(vtype="B", name=f"v_{p}_{s}")
    
    for t in range(n_T):
        
        model.addCons(
            sum(w[s][t] * v[p][s]  for p in range(n_L) for s in range(n_S)) >= n_D[t]
        )
    for p in range(n_L):
        for s in range(n_S):
            model.addCons(v[p][s] <= u_values[p][s])
    for p in range(n_L):
        model.addCons(
            sum(v[p][s] for s in range(n_S)) <= 1
        )
        

        # 目的関数の設定
    model.setObjective(
        sum(
            sum(w[s][t] * v[p][s]  for p in range(n_L) for s in range(n_S)) - n_D[t] for t in range(n_T)
            ),
        "minimize"
    )

    # 最適化の実行
    model.optimize()
    end = time.perf_counter()

    # ---- 結果の処理 ----
    if model.getStatus() == "optimal":
        ret[1]=1
        optimal_value = model.getObjVal()  # 現在のOptimalValueを取得
        #optimal_value.append(optimal_value)  # リストに保存

            # v_valuesの更新
        for p in range(n_L):       
            for s in range(n_S):
                v_values[p][s] = model.getVal(v[p][s])  # vの値を更新
        
        for p in range(n_L):
            work_satisfaction[p] = sum(w[s][t] * v_values[p][s] * h_P[p][t] for t in range(n_T) for s in range(n_S))

    else:
        print("Problem could not be solved to optimality")
        ret[1] = 0


    # 問題の定義
    '''
    problem1 = LpProblem("Shift_Assignment", LpMinimize)
    problem2 = LpProblem("Shift_Assignment", LpMaximize)

    # 変数の設定
    x = LpVariable.dicts("x", range(n_S), lowBound=0, cat='Integer')  # シフトパターンに割り当てる人数
    y = LpVariable.dicts("y", (range(n_L), range(n_S)), cat='Binary')  # 従業員がシフトパターンに割り当てられているか
    '''

    #返り値
    #[1段階目成功可否,2段階目成功可否,超過人時,希望充足時]
    
    ret[0]=1
    
    


        # ---- ループの回数とOptimalValueの遷移を表示 ----
    print("Optimal value transitions:")


    # ---- 最終結果の表示 ----
    print("\nFinal Summary:")

    # 各従業員の結果を出力
    
    for p in range(n_L):
        print(f"従業員 {p}:")
        
        # 割り当てられたシフトを表示
        assigned_shifts = [s for s in range(n_S) if u_values[p][s] == 1.0]
        print(f"  割り当てられたシフト: {assigned_shifts}")
    if model.getStatus() == "optimal":
        for p in range(n_L):
            # v[p]の勤務シフトを出力する
            for s in range(n_S):
                if v_values[p][s] == 1:
                    print(f"  勤務するシフト:{s:.0f}")
                    print(f"  勤務充足度: {work_satisfaction[p]:.2f}")
        print(f"勤務充足度合計:  {sum(work_satisfaction[p] for p in range(n_L))}")
        labor_positive_sum = sum(v_values[l][s] * w[s][t] * h_P[l][t] for l in range(n_L) for s in range(n_S) for t in range(n_T))
        want_work = sum(h_P[l][t] for l in range(n_L) for t in range(n_T))/(n_L*n_T)
        ret[3] = labor_positive_sum /(sum(w[s][t] * v_values[l][s] for s in range(n_S) for t in range(n_T) for l in range(n_L)) * want_work)
        
        
    
    # 超過人数の計算（修正後）
    total_excess = sum(
        max(0, sum((w[s][t] * v_values[p][s] * u_values[p][s])for p in range(n_L) for s in range(n_S)) - n_D[t]) 
         for t in range(n_T)
         )
    print(f"超過人数:  {total_excess}")
    print('計測時間{:.2f}'.format((end-start)*1000)) 
    ret[2] = total_excess/sum(n_D[t] for t in range(n_T))
    ret[4] = (end-start)*1000
    return ret