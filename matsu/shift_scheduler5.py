"""
pyscipopt
必要人数優先(勤務不可での勤務はペナルティ)
第一段階:従業員毎にシフトパターンを割り付け(勤務希望最大化)
第二段階:従業員がどのシフトパターンで勤務するか(超過人数最小化)
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


class ShiftScheduler5(ShiftScheduler):
    def solve(self):
        u_values ={l:{s: 0 for s in range(self.n_S)}for l in range(self.n_L)}
        v_values ={l:{s: 0 for s in range(self.n_S)}for l in range(self.n_L)}


        #返り値
        #[1段階目成功可否,2段階目成功可否,超過人時,希望充足時,時間指標]


        #################１段目#################

        # 目的関数: 勤務希望時間帯の多いシフトパターンから割り付け
        a = 40
        omega = 1000
        for l in range(self.n_L):
            model = Model(f"assign_u_l_{l}")
            u = {}
            for s in range(self.n_S):
                u[s] = model.addVar(vtype="B",name=f"u_{l}_{s}")
            
            ##aこシフトパターンを割り付ける
            model.addCons(sum(u[s] for s in range(self.n_S)) == a)
            model.setObjective(
                sum((self.w[s][t]*u[s]*self.h_P[l][t] )for s in range(self.n_S)for t in range(self.n_T)for l in range(self.n_L))
                -omega*sum((self.w[s][t]*u[s]*self.h_N[l][t] )for s in range(self.n_S)for t in range(self.n_T)for l in range(self.n_L)),"maximize"
            )
            model.optimize()
            if model.getStatus() == "optimal":
                for s in range(self.n_S):
                    u_values[l][s] = model.getVal(u[s])
                self.ret[0] = 1
                
            else:
                print("Problem1 could not be solved to optimality")
                for s in range(self.n_S):
                    u_values[l][s]=0
                self.ret[0] = 0
        


        #################２段目#################
        model=Model("2nd")
        v = {}
        omega = 10000
        for l in range(self.n_L):
            v[l] = {}
            for s in range(self.n_S):
                v[l][s] = model.addVar(vtype="B",name=f"v_{l}_{s}")
        
        """
        model.addCons(
            sum(self.w[s][t] * y[l][s] * self.h_N[l][t] for s in range(self.n_S) for t in range(self.n_T) for l in range(self.n_L)) == 0
        )
        """
        ##不足人数が出てはならない
        for t in range(self.n_T):
            model.addCons(
                sum(v[l][s]*self.w[s][t] for l in range(self.n_L) for s in range(self.n_S)) -self.n_D[t] >=0
            )
        ##従業員は勤務可能シフトで勤務する
        for l in range(self.n_L):
            for s in range(self.n_S):
                model.addCons(
                    u_values[l][s] >= v[l][s]
                )
        ##勤務するシフトパターンは一つ以下でなければならない
        for l in range(self.n_L):
            model.addCons(
                sum(v[l][s] for s in range(self.n_S)) <= 1
            )
        model.setObjective(
            sum(sum(self.w[s][t]*v[l][s] for s in range(self.n_S)for l in range(self.n_L))-self.n_D[t] for t in range(self.n_T)) 
            + omega*sum((self.w[s][t] * v[l][s] * self.h_N[l][t] ) for s in range(self.n_S) for t in range(self.n_T) for l in range(self.n_L)),"minimize"
        )

        start = time.perf_counter()
        model.optimize()
        end = time.perf_counter()

        if model.getStatus() == "optimal":
            self.ret[1] = 1
            for l in range(self.n_L):
                for s in range(self.n_S):
                    v_values[l][s] = model.getVal(v[l][s])
            assigned_shifts = [100] * self.n_L
            for l in range(self.n_L):
                for s in range(self.n_S):
                    if v_values[l][s] == 1:
                        assigned_shifts[l] = s
            print(f"２階目の従業員の割り当て:{assigned_shifts}")
            labor_positive_sum = sum((self.w[s][t] * v_values[l][s] * self.h_P[l][t]) 
                                 for l in range(self.n_L) for s in range(self.n_S) for t in range(self.n_T))
            want_work = sum(self.h_P[l][t] for l in range(self.n_L) for t in range(self.n_T))/(self.n_L*self.n_T)
            self.ret[3] = labor_positive_sum /self.n_L
            print("従業員満足度:",labor_positive_sum)
            self.ret[5] =  sum((self.w[s][t] * v_values[l][s] * self.h_N[l][t]) 
                               for l in range(self.n_L) for s in range(self.n_S) for t in range(self.n_T)) 
            print("勤務不可での勤務:",self.ret[5])
        
        else:
            print("Problem2 could not be solved to optimality")
            self.ret[1] = 0

        print('計測時間{:.2f}'.format((end-start)*1000)) 
        self.ret[4] = (end-start)*1000
        

        

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
