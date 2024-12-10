"""
1段階目:各シフトパターンに割り当てる人数を確定
2段階目:従業員を各シフトパターンに割り付ける
という順でシフトを作成するプログラム
"""
import numpy as np
from pulp import LpProblem, LpVariable, LpMinimize,LpMaximize, lpSum, LpStatus, LpStatusOptimal,PULP_CBC_CMD, value
from program.matsu.shift_scheduler import ShiftScheduler


class ShiftScheduler1(ShiftScheduler):
    def solve(self):
        # 問題の定義
        problem1 = LpProblem("Shift_Assignment", LpMinimize)
        problem2 = LpProblem("Shift_Assignment", LpMaximize)

        # 変数の設定
        x = LpVariable.dicts("x", range(self.n_S), lowBound=0, cat='Integer')  # シフトパターンに割り当てる人数
        y = LpVariable.dicts("y", (range(self.n_L), range(self.n_S)), cat='Binary')  # 従業員がシフトパターンに割り当てられているか

        #返り値
        #[1段階目成功可否,2段階目成功可否,超過人時,希望充足時]


        #################１段目#################

        # 目的関数: 超過人数の最小化
        problem1 += lpSum([lpSum([self.w[s][t] * x[s] for s in range(self.n_S)]) - self.n_D[t] for t in range(self.n_T)])

        # 制約条件の設定
        for t in range(self.n_T):
            problem1 += lpSum([lpSum([self.w[s][t] * x[s] for s in range(self.n_S)])]) >= self.n_D[t]  # 各時間帯の必要人数

        # 問題の解決
        problem1.solve(PULP_CBC_CMD(msg=False))
        self.ret[0]=problem1.status

        #################２段目#################


        # 目的関数: 従業員の希望の最大化
        problem2 += lpSum([lpSum([lpSum([y[l][s] * self.w[s][t] * self.h_P[l][t] for s in range(self.n_S)])] for t in range(self.n_T))] for l in range(self.n_L))

        for l in range(self.n_L):
            for t in range(self.n_T):
                problem2 += lpSum([y[l][s] * self.w[s][t] * self.h_N[l][t] for s in range(self.n_S)]) == 0  # 各従業員のシフトパターン制約

        for s in range(self.n_S):
            problem2 += lpSum([y[l][s] for l in range(self.n_L)]) == value(x[s])  # シフトパターンに必要人数

        for l in range(self.n_L):
            problem2 += lpSum([y[l][s] for s in range(self.n_S)]) <= 1  # 割り付けるシフトパターンは一個まで

        # 問題の解決
        problem2.solve(PULP_CBC_CMD(msg=False))
        self.ret[1]=problem2.status
        self.ret[2]=sum(sum(self.w[s][t]*value(x[s]) for s in range(self.n_S))-self.n_D[t] for t in range(self.n_T))
        self.ret[3]=value(problem2.objective)/self.n_L

        assigned_shifts = []
        for l in range(self.n_L):
            unallocated=True
            for s in range(self.n_S):
                if value(y[l][s]) == 1 :
                    assigned_shifts.append(s+1)
                    unallocated=False
                    break
            if unallocated:
                assigned_shifts.append(-1)
        self.ret.append(assigned_shifts)
