"""
pyscipopt
必要人数優先(勤務不可での勤務はペナルティ)
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


from pulp import LpProblem, LpVariable, LpMinimize,LpMaximize, lpSum, LpStatus, LpStatusOptimal,PULP_CBC_CMD, value
from mojule.shift_scheduler import ShiftScheduler


class ShiftScheduler4(ShiftScheduler):
    def solve(self):
        x_values ={s:0 for s in range(self.n_S)}
        y_values ={l:{s: 0 for s in range(self.n_S)}for l in range(self.n_L)}


        #返り値
        #[1段階目成功可否,2段階目成功可否,超過人時,希望充足時,時間指標]


        #################１段目#################

        # 目的関数: 超過人数の最小化
        model = Model("1st")
        x ={}
        for s in range(self.n_S):
            x[s] = model.addVar(f"x_{s}",vtype = "I")
        for t in range(self.n_T):
            model.addCons(sum(self.w[s][t]*x[s] for s in range(self.n_S)) >= self.n_D[t])
        model.addCons(x[s] >= 0)
        model.setObjective(
            sum(sum(self.w[s][t]*x[s] for s in range(self.n_S))-self.n_D[t] for t in range(self.n_T)),"minimize"
        )
        start = time.perf_counter()
        model.optimize()
        end = time.perf_counter()
        self.ret[7] = (end-start)*1000
        if model.getStatus() == "optimal":
            for s in range(self.n_S):
                x_values[s] = model.getVal(x[s])
            self.ret[0] = 1
            if self.print_log:
                print(f"各シフトパターンの割り付け人数：{x_values}")
        else:
            print("Problem1 could not be solved to optimality")
            self.ret[0] = 0


        #################２段目#################
        model=Model("2nd")
        y = {}
        omega_1 = 1/(self.n_S*self.n_T*self.n_L)
        omega_2 = 1
        for l in range(self.n_L):
            y[l] = {}
            for s in range(self.n_S):
                y[l][s] = model.addVar(vtype="B",name=f"y_{l}_{s}")
        
        """
        model.addCons(
            sum(self.w[s][t] * y[l][s] * self.h_N[l][t] for s in range(self.n_S) for t in range(self.n_T) for l in range(self.n_L)) == 0
        )
        """
        for s in range(self.n_S):
            model.addCons(
                sum(y[l][s] for l in range(self.n_L)) == x_values[s]
            )
        for l in range(self.n_L):
            model.addCons(
                sum(y[l][s] for s in range(self.n_S)) <= 1
            )
        model.setObjective(
            sum((omega_1*self.w[s][t] * y[l][s] * self.h_P[l][t] - omega_2*self.w[s][t] * y[l][s] * self.h_N[l][t]) for s in range(self.n_S) for t in range(self.n_T) for l in range(self.n_L)),"maximize"
        )

        start = time.perf_counter()
        model.optimize()
        end = time.perf_counter()

        if model.getStatus() == "optimal":
            self.ret[1] = 1
            for l in range(self.n_L):
                for s in range(self.n_S):
                    y_values[l][s] = model.getVal(y[l][s])
            '''
            assigned_shifts = [100] * self.n_L
            for l in range(self.n_L):
                for s in range(self.n_S):
                    if y_values[l][s] == 1:
                        assigned_shifts[l] = s
            '''
            ##print(f"２階目の従業員の割り当て:{assigned_shifts}")
            labor_positive_sum = sum((self.w[s][t] * y_values[l][s] * self.h_P[l][t]) 
                                 for l in range(self.n_L) for s in range(self.n_S) for t in range(self.n_T))
            want_work = sum(self.h_P[l][t] for l in range(self.n_L) for t in range(self.n_T))/(self.n_L*self.n_T)
            self.ret[3] = labor_positive_sum /self.n_L
            print("従業員満足度:",labor_positive_sum)
            self.ret[6] =  sum((self.w[s][t] * y_values[l][s] * self.h_N[l][t]) 
                               for l in range(self.n_L) for s in range(self.n_S) for t in range(self.n_T)) 
            ##print("勤務不可での勤務:",self.ret[6])
        
        else:
            print("Problem2 could not be solved to optimality")
            self.ret[1] = 0

        print('計測時間{:.2f}'.format((end-start)*1000)) 
        self.ret[8] = (end-start)*1000
        

        

        # 問題の解決
        ##超過人数の代入
        self.ret[2] =  sum(sum(self.w[s][t]*y_values[l][s] for l in range(self.n_L) for s in range(self.n_S))- self.n_D[t] for t in range(self.n_T))

        assigned_shifts = []
        for l in range(self.n_L):
            unallocated=True
            for s in range(self.n_S):
                if y_values[l][s] == 1 :
                    assigned_shifts.append(s+1)
                    unallocated=False
                    break
            if unallocated:
                assigned_shifts.append(-1)
        self.ret.append(assigned_shifts)
        self.ret[5]=assigned_shifts
        num_person_per_shift = [0]*self.n_S
        for s in range(self.n_S):
            for l in range(self.n_L):
                if y_values[l][s] == 1:
                    num_person_per_shift[s] += 1
        self.ret[4]=([int(num_person_per_shift[s]) for s in range(self.n_S)])
        '''
        for s in range(self.n_S):
            for l in range(self.n_L):
                if v_values[l][s] == 1:
                    print(f"v_{l}_{s}")
        '''
