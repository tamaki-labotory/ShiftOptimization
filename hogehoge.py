##ただの確認用のプログラムです

import json
from typing import List
import numpy as np

with open("/Users/matsumura/Desktop/修論/solver/json/shift_data132.json", "r") as f:
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
M:int=1001001001

def get_fitness1(x) -> float:
    ret=0
    for l in range(n_L):
        if x[l]==-1:
                continue
        for t in range(n_T):
            if w[x[l]-1][t]*h_N[l][t]==1:
                  print(f"l{l+1},t{t+1}")
            ret+=w[x[l]-1][t]*(h_P[l][t] - h_N[l][t]*M) 

    return ret

def get_fitness2(x) -> float:
    """
    各シフト割り付けに対し、目的関数2の評価値を計算

    """

    #各時間帯で働く人数を計算
    ret=[0]*n_T
    for l in range(n_L):
        if x[l]==-1:
                    continue  
        for t in range(n_T):
            ret[t]+=w[x[l]-1][t]
    for t in range(n_T):
        ret[t]-=n_D[t]

    #不足人数に対し、超過人数より割増しで低い評価をつける
    ret=[ret[t]+np.exp(-ret[t]*1000) for t in range(n_T)]

    return -sum(ret)





data=[-1, 3, 4, 4, 7, 7, 4, 3, 4, 4, 7, 3, -1, 4, -1, -1]
#超過人数・不足人数計算
over_labors=under_labors=0
workers=[0]*n_T
for l in range(n_L):
    if data[l]==-1:
                continue  
    for t in range(n_T):
        workers[t]+=w[data[l]-1][t]
for t in range(n_T):
    if workers[t]-n_D[t]<0:
        under_labors-=workers[t]-n_D[t]
    else:
        over_labors+=workers[t]-n_D[t]

fitness: List[float] = [get_fitness1(data),get_fitness2(data)]
print(f'シフト割り付け:{data}, 超過人数:{over_labors}, 不足人数:{under_labors}, 従業員満足度:{fitness[0]/n_L}, fitness:{fitness}')