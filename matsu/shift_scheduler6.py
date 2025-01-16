"""
pyscipopt
一段階最適化(勤務不可での勤務はペナルティ)
"""
import sys
import time

# passの設定 (pip showで出てきた、LocationのPASSを以下に設定)
sys.path.append('/Users/hymac/mypy/lib/python3.12/site-packages')
import json
import math
import numpy as np
from pyscipopt import Model


from pulp import LpProblem, LpVariable, LpMinimize,LpMaximize, lpSum, LpStatus, LpStatusOptimal,PULP_CBC_CMD, value
from mojule.shift_scheduler import ShiftScheduler


class ShiftScheduler6(ShiftScheduler):
    def solve(self):
        v_values ={l:{s: 0 for s in range(self.n_S)}for l in range(self.n_L)}


        #返り値
        #[1段階目成功可否,2段階目成功可否,超過人時,希望充足時,時間指標]


        #################１段目#################

        # 目的関数: 超過人数の最小化
        model = Model("1st")
        omega_1 = 1/(self.n_S*self.n_T*self.n_L)
        omega_2 = 1
        omega_3 = 1
        phi_1 = 1
        phi_2 = 1
        phi_3 = 1

        v ={}
        for l in range(self.n_L):
            v[l] = {}
            for s in range(self.n_S):
                v[l][s] = model.addVar(vtype="B",name=f"v_{l}_{s}")
        for t in range(self.n_T):
            model.addCons(sum(self.w[s][t]*v[l][s] for s in range(self.n_S) for l in range(self.n_L)) >= self.n_D[t])
        for l in range(self.n_L):
            model.addCons(sum(v[l][s] for s in range(self.n_S)) <= 1)
        model.setObjective(
            omega_3*sum(sum(self.w[s][t]*v[l][s] for s in range(self.n_S)for l in range(self.n_L))-self.n_D[t] for t in range(self.n_T))
            +omega_2*sum(v[l][s]*self.w[s][t]*self.h_N[l][t] for l in range(self.n_L)for s in range(self.n_S)for t in range(self.n_T))
            -omega_1*sum(v[l][s]*self.w[s][t]*self.h_P[l][t] for l in range(self.n_L)for s in range(self.n_S)for t in range(self.n_T)),"minimize"
        )
        start = time.perf_counter()
        model.optimize()
        end = time.perf_counter()
        self.ret[1] = 1

        if model.getStatus() == "optimal":
            for s in range(self.n_S):
                for l in range(self.n_L):
                    v_values[l][s] = model.getVal(v[l][s])
            self.ret[0] = 1
            over_labors = sum(sum(self.w[s][t]*v_values[l][s] for s in range(self.n_S)for l in range(self.n_L))-self.n_D[t] for t in range(self.n_T))
            #self.ret[2] = over_labors/sum(self.n_D[t] for t in range(self.n_T))
            self.ret[2] = over_labors

            if self.print_log:
                print(f"超過人数：{over_labors}")
                ##print(f"各シフトパターンの割り付け人数：{v_values}")
            labor_positive_sum = sum((self.w[s][t] * v_values[l][s] * self.h_P[l][t]) 
                                 for l in range(self.n_L) for s in range(self.n_S) for t in range(self.n_T))
            self.ret[3] = labor_positive_sum /self.n_L
            ##print("従業員満足度:",labor_positive_sum)
            self.ret[6] =  sum((self.w[s][t] * v_values[l][s] * self.h_N[l][t]) 
                               for l in range(self.n_L) for s in range(self.n_S) for t in range(self.n_T)) 
            ##print("勤務不可での勤務:",self.ret[6])
        else:
            print("Problem1 could not be solved to optimality")
            self.ret[0] = 0
        print('計測時間{:.2f}'.format((end-start)*1000)) 
        self.ret[7] = (end-start)*1000     

        # 問題の解決

        assigned_shifts = []
        for l in range(self.n_L):
            unallocated=True
            for s in range(self.n_S):
                if v_values[l][s] == 1 :
                    assigned_shifts.append(s+1)
                    unallocated=False
                    break
            if unallocated:
                assigned_shifts.append(-1)
        self.ret.append(assigned_shifts)
        #self.ret[4]=([int(value(x[v])) for v in x])
        self.ret[5]=assigned_shifts
        num_pserson_per_shift = [0]*self.n_S
        for s in range(self.n_S):
            for l in range(self.n_L):
                if v_values[l][s] == 1:
                    num_pserson_per_shift[s] += 1
        self.ret[4]=([int(num_pserson_per_shift[s]) for s in num_pserson_per_shift])
        for s in range(self.n_S):
            for l in range(self.n_L):
                if v_values[l][s] == 1:
                    print(f"v_{l}_{s}")
