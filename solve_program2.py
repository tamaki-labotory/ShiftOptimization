"""
1段階目:
2段階目:
という順でシフトを作成するプログラム
"""

import json
import numpy as np
from pulp import LpProblem, LpVariable, LpMinimize,LpMaximize, lpSum, LpStatus, LpStatusOptimal, value

def solve(file_path):

    # JSONファイルからデータを読み込む
    with open(file_path, "r") as f:
        shift_data = json.load(f)

    # 読み込んだデータの表示
    print("Required Employees per Time Slot:")
    print(shift_data["required_employees"])

    print("\nShift Patterns:")
    for i, pattern in enumerate(shift_data["shift_patterns"]):
        print(f"Pattern {i+1}: {pattern}")

    print("\nPreferences:")
    for i, preference in enumerate(shift_data["preferences"]):
        print(f"Employee {i+1}: {preference}")

    print("\nUnavailable Slots:")
    for i, unavailable in enumerate(shift_data["unavailable_slots"]):
        print(f"Employee {i+1}: {unavailable}")

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

    # 問題の定義
    problem1 = LpProblem("Shift_Assignment", LpMinimize)
    problem2 = LpProblem("Shift_Assignment", LpMaximize)

    # 変数の設定
    x = LpVariable.dicts("x", range(n_L), lowBound=0, cat='Integer')  # シフトパターンに割り当てる人数
    y = LpVariable.dicts("y", (range(n_L), range(n_S)), cat='Binary')  # 従業員がシフトパターンに割り当てられているか



    #################１段目#################

    # 目的関数: 超過人数の最小化
    problem1 += lpSum([lpSum([w[s][t] * x[s] for s in range(n_S)]) - n_D[t] for t in range(n_T)])

    # 制約条件の設定
    for t in range(n_T):
        problem1 += lpSum([lpSum([w[s][t] * x[s] for s in range(n_S)])]) >= n_D[t]  # 各時間帯の必要人数

    # 問題の解決
    print(problem1)
    problem1.solve()


    #################２段目#################


    # 目的関数: 従業員の希望の最大化
    problem2 += lpSum([lpSum([lpSum([y[l][s] * w[s][t] * h_P[l][t] for s in range(n_S)])] for t in range(n_T))] for l in range(n_L))

    for l in range(n_L):
        for t in range(n_T):
            problem2 += lpSum([y[l][s] * w[s][t] * h_N[l][t] for s in range(n_S)]) == 0  # 各従業員のシフトパターン制約

    for s in range(n_S):
        problem2 += lpSum([y[l][s] for l in range(n_L)]) == value(x[s])  # シフトパターンに必要人数

    for l in range(n_L):
        problem2 += lpSum([y[l][s] for s in range(n_S)]) <= 1  # 割り付けるシフトパターンは一個まで

    # 問題の解決
    problem2.solve()


    # 結果の表示
    if problem1.status == 1:
        print("１階目の最適解が見つかりました。")
        print("超過人数:", value(problem1.objective))
        print("各シフトパターンの割り当て人数:")
        for s in range(n_S):
            print(f"シフトパターン {s+1}: {value(x[s])}")
    else:
        print("１階目の最適解は見つかりませんでした。")

    if problem2.status == 1:
        print("２階目の従業員の割り当て:")
        for l in range(n_L):
            assigned_shifts = [s + 1 for s in range(n_S) if value(y[l][s]) == 1]
            print(f"従業員 {l+1}: シフト {assigned_shifts}")
        print("従業員満足度:",value(problem2.objective))
    else:
        print("２階目の最適解は見つかりませんでした。")