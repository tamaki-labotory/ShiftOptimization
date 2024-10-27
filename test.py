
from pulp import LpProblem, LpVariable, LpMinimize,LpMaximize, lpSum, LpStatus, LpStatusOptimal, value

# 定数の設定
n_S = 3  # シフトパターン数
n_T = 4  # 時間帯数
n_L = 5  # 従業員数

# 時間帯当たり必要人数
n_D = [2, 3, 1, 2]  # 各時間帯に必要な人数

# 各シフトパターンの時間帯の必要人数（1: 必要、0: 不要）
w = [[1, 1, 0, 0],  # シフトパターン1
     [1, 0, 1, 0],  # シフトパターン2
     [0, 1, 1, 1]]  # シフトパターン3

# 従業員の勤務希望（1: 希望、0: 不希望）
h_P = [[1, 1, 0, 0],  # 従業員1の希望
       [1, 0, 1, 0],  # 従業員2の希望
       [0, 1, 1, 1],  # 従業員3の希望
       [1, 1, 1, 0],  # 従業員4の希望
       [0, 0, 1, 1]]  # 従業員5の希望

# 従業員の勤務不可能（1: 不可、0: ？）
h_N = [[0, 0, 0, 1],  # 従業員1の希望
       [0, 0, 0, 0],  # 従業員2の希望
       [0, 0, 0, 0],  # 従業員3の希望
       [0, 0, 0, 0],  # 従業員4の希望
       [1, 0, 0, 0]]  # 従業員5の希望

# 問題の定義
problem1 = LpProblem("Shift_Assignment", LpMinimize)
problem2 = LpProblem("Shift_Assignment", LpMaximize)

# 変数の設定
x = LpVariable.dicts("x", range(n_L), lowBound=0, cat='Integer')  # シフトパターンに割り当てる人数
y = LpVariable.dicts("y", (range(n_L), range(n_S)), cat='Binary')  # 従業員がシフトパターンに割り当てられているか

# 目的関数: 超過人数の最小化
problem1 += lpSum([lpSum([w[s][t] * x[s] for s in range(n_S)]) - n_D[t] for t in range(n_T)])

# 目的関数: 従業員の希望の最大化


# 制約条件の設定
for t in range(n_T):
    problem1 += lpSum([lpSum([w[s][t] * x[s] for s in range(n_S)])]) >= n_D[t]  # 各時間帯の必要人数

# 問題の解決
print(problem1)
problem1.solve()


problem2 += lpSum([lpSum([lpSum([y[l][s] * w[s][t] * h_P[l][t] for s in range(n_S)])] for t in range(n_T))] for l in range(n_L))

for l in range(n_L):
    for t in range(n_T):
        problem2 += lpSum([y[l][s] * w[s][t] * h_N[l][t] for s in range(n_S)]) == 0  # 各従業員のシフトパターン制約

for s in range(n_S):
    problem2 += lpSum([y[l][s] for l in range(n_L)]) >= value(x[s])  # シフトパターンに必要人数

for l in range(n_L):
    problem2 += lpSum([y[l][s] for s in range(n_S)]) <= 1  # 割り付けるシフトパターンは一個まで

# 問題の解決
problem2.solve()

# 結果の表示
if problem1.status == 1:
    print("最適解が見つかりました。")
    print("超過人数:", value(problem1.objective))
    print("各シフトパターンの割り当て人数:")
    for s in range(n_S):
        print(f"シフトパターン {s+1}: {value(x[s])}")
    print("従業員の割り当て:")
    for l in range(n_L):
        assigned_shifts = [s + 1 for s in range(n_S) if value(y[l][s]) == 1]
        print(f"従業員 {l+1}: シフト {assigned_shifts}")
    print("従業員満足度:",value(problem2.objective))
else:
    print("最適解は見つかりませんでした。")