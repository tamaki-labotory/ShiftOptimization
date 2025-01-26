"""
pyscipopt
不足人数が0であることを制約に勤務人数を最小化するための
シフトパターンあたり必要人数を求める
"""
import sys
import time

# passの設定 (pip showで出てきた、LocationのPASSを以下に設定)
sys.path.append('/Users/hymac/mypy/lib/python3.12/site-packages')
import json
import math
import numpy as np
from pyscipopt import Model






file_paths = {
    "shift_patterns": "/Users/hymac/mypy/ShiftOptimization-progress1/json/shift_patterns_1.json",
    "preferences_and_unavailable_slots": "/Users/hymac/mypy/ShiftOptimization-progress1/json/preferences_and_unavailable_slots_1.json",
    "required_employees": "/Users/hymac/mypy/ShiftOptimization-progress1/json/required_employees_1.json"
    }
# データの読み込み
with open(file_paths["shift_patterns"], "r") as f:
    shift_patterns = json.load(f)["shift_patterns"]

with open(file_paths["required_employees"], "r") as f:
    required_employees = json.load(f)["required_employees"]

n_S = np.array(shift_patterns).shape[0]  # シフトパターン数
n_T = np.array(shift_patterns).shape[1]  # 時間帯数
w = shift_patterns
n_D = required_employees
x_values ={s:0 for s in range(n_S)}


    # 目的関数: 超過人数の最小化
model = Model("1st")
x ={}
for s in range(n_S):
    x[s] = model.addVar(f"x_{s}",vtype = "I")
for t in range(n_T):
    model.addCons(sum(w[s][t]*x[s] for s in range(n_S)) >= n_D[t])
for s in range(n_S):
      model.addCons(x[s] >= 0)
model.setObjective(
    sum(x[s] for s in range(n_S)),"minimize"
    )
    #start = time.perf_counter()
model.optimize()
#end = time.perf_counter()
if model.getStatus() == "optimal":
    for s in range(n_S):
        x_values[s] = model.getVal(x[s])
            
    print(f"各シフトパターンの割り付け人数：{x_values}")
else:
    print("Problem1 could not be solved to optimality")
            


        
