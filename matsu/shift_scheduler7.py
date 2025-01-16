"""
pyscipopt
必要人数優先(勤務不可での勤務はペナルティ)
第一段階:従業員毎にシフトパターン希望優先度を割り付け(勤務希望最大化,勤務不可最小化)
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
from pyscipopt import quicksum


from pulp import LpProblem, LpVariable, LpMinimize,LpMaximize, lpSum, LpStatus, LpStatusOptimal,PULP_CBC_CMD, value
from mojule.shift_scheduler import ShiftScheduler


class ShiftScheduler7(ShiftScheduler):
    def solve(self):
        u_values ={l:{s:{k: 0 for k in range(self.n_S)}  for s in range(self.n_S)}for l in range(self.n_L)}
        u_values_2 ={l:{s: 0 for s in range(self.n_S)}for l in range(self.n_L)}
        v_values ={l:{s: 0 for s in range(self.n_S)}for l in range(self.n_L)}


        #返り値
        #[1段階目成功可否,2段階目成功可否,超過人時,希望充足時,時間指標]


        #################１段目#################

        # 目的関数: 勤務希望時間帯の多いシフトパターンから割り付け
        a = 40
        omega_1 = 1/(self.n_S*self.n_T*self.n_L)
        omega_2 = 1
        omega_3 = 1
        phi_1 = 1
        phi_2 = 1
        phi_3 = 1
        phi_4 = self.n_T/self.n_S
        phi_5 = self.n_T*self.n_L/self.n_S
        # k-1回目までに選ばれたsを記録する集合
        """
        for l in range(self.n_L):
            for k in range(self.n_S):
                model = Model(f"assign_u_{l}_{k}")
                u = {}
                for s in range(self.n_S):
                    u[s] = model.addVar(vtype="B", name=f"u_{l}_{s}_{k}")

                # すでに選ばれたsにはu[s] = 0の制約を追加
                for s in assigned_s[l]:
                    model.addCons(u[s] == 0)

                # 各従業員ごとに1つのシフトパターンのみを割り当て
                model.addCons(sum(u[s] for s in range(self.n_S)) == 1)

                # 目的関数（修正済み）
                positive_term = sum(self.w[s][t] * u[s] * self.h_P[l][t] for s in range(self.n_S) for t in range(self.n_T))
                negative_term = sum(self.w[s][t] * u[s] * self.h_N[l][t] for s in range(self.n_S) for t in range(self.n_T))

                model.setObjective(
                    omega_1 * phi_1 * positive_term - omega_2 * phi_2 * negative_term,
                    "maximize"
                )


                model.optimize()

                # 最適解が見つかったら、選ばれたsを記録
                if model.getStatus() == "optimal":
                    for s in range(self.n_S):
                        if model.getVal(u[s]) == 1:
                            assigned_s[l].add(s)  # 次回のループで禁止
                            u_values[l][s][k] = 1
                    self.ret[0] = 1
                else:
                    print("Problem1 could not be solved to optimality")
                    for s in range(self.n_S):
                        u_values[l][s] = 0
                    self.ret[0] = 0
            
            for l in range(self.n_L):
                for s in range(self.n_S):
                    for k in range(self.n_S):
                        if u_values[l][s][k] == 1:
                            u_values_2[l][s] == k
            

        for l in range(self.n_L):
            for s in range(self.n_S):
                if u_values_2[l][s] >= 1:
                    print(f"{l}_{s} == {u_values_2[l][s]}")
           
        print(u_values_2)

            
                
            
        

        """

        M = 100000  # 動的に計算するのが望ましい
        for l in range(self.n_L):
            model = Model(f"assign_u_{l}")
            u = {}
            for s in range(self.n_S):
                u[s] = {}
                for k in range(self.n_S):
                    u[s][k] = model.addVar(vtype="B", name=f"u_{l}_{s}_{k}")
            
            # 全てのシフトパターンに順位が定められる
            for s in range(self.n_S):
                model.addCons(sum(u[s][k] for k in range(self.n_S)) == 1)

            # ある順位では一つのシフトパターンのみを選択する
            for k in range(self.n_S):
                model.addCons(sum(u[s][k] for s in range(self.n_S)) == 1)

            positive_term = {
                s: sum(self.w[s][t] * self.h_P[l][t] for t in range(self.n_T))
                for s in range(self.n_S)
            }
            negative_term = {
                s: sum(self.w[s][t] * self.h_N[l][t] for t in range(self.n_T))
                for s in range(self.n_S)
            }

            # 順位制約（修正済み）
            for s in range(self.n_S):
                for s_2 in range(self.n_S):
                    for k in range(self.n_S - 1):  # k < k'
                        model.addCons(
                            omega_1 * phi_1 * positive_term[s] - omega_2 * phi_2 * negative_term[s] + M * (2 - u[s][k] - u[s_2][k + 1])
                            >= omega_1 * phi_1 * positive_term[s_2] - omega_2 * phi_2 * negative_term[s_2]
                        )

            # 目的関数（修正済み）
            model.setObjective(
                sum(u[s][k] * (omega_1 * phi_1 * positive_term[s] - omega_2 * phi_2 * negative_term[s]) for s in range(self.n_S) for k in range(self.n_S)),
                "maximize"
            )

            #start = time.perf_counter()
            model.optimize()
            #end = time.perf_counter()

            # 結果確認
            if model.getStatus() == "optimal":
                print(f"Optimal solution found for employee {l}")
                print("Assigned shifts and ranks:")
                self.ret[0] = 1

                # 結果を格納するリスト
                assigned_ranks = []

                for s in range(self.n_S):
                    for k in range(self.n_S):
                        if model.getVal(u[s][k]) > 0.5:  # u[s][k] が選ばれている場合
                            assigned_ranks.append((k + 1, s + 1))  # 人間にわかりやすい1始まりの表示
                            u_values[l][s][k] = 1

                # 順位でソート
                assigned_ranks.sort(key=lambda x: x[0])

                # 結果の出力
                for rank, shift in assigned_ranks:
                    print(f"Rank {rank}: Shift pattern {shift}")
            else:
                print(f"No optimal solution found for employee {l}. Status: {model.getStatus()}")
                self.ret[0] = 0


            
            
            
            for s in range(self.n_S):
                for k in range(self.n_S):
                    if u_values[l][s][k] == 1:
                        u_values_2[l][s] = k
        """    
        for l in range(self.n_L):
            for s in range(self.n_S):
                if u_values_2[l][s] >= 1:
                    print(f"{l}_{s} == {u_values_2[l][s]}")
        """   

        #################２段目#################
        model=Model("2nd")
        v = {}
        omega = 10000
        z = model.addVar(vtype = "I",name = "z")
        for l in range(self.n_L):
            v[l] = {}
            for s in range(self.n_S):
                v[l][s] = model.addVar(vtype="B",name=f"v_{l}_{s}")
        
        
        #model.addCons(
        #    sum(self.w[s][t] * y[l][s] * self.h_N[l][t] for s in range(self.n_S) for t in range(self.n_T) for l in range(self.n_L)) == 0
        #)
        
        ##不足人数が出てはならない
        for t in range(self.n_T):
            model.addCons(
                sum(v[l][s]*self.w[s][t] for l in range(self.n_L) for s in range(self.n_S)) -self.n_D[t] >=0
            )
        
        ##勤務するシフトパターンは一つ以下でなければならない
        for l in range(self.n_L):
            model.addCons(
                sum(v[l][s] for s in range(self.n_S)) <= 1
            )
        
        ##
        omega_3 = 1
        omega_4 = 1
        omega_5= 1/self.n_S
        '''
        #zは実際に勤務する中で最も低い勤務希望度である
        for l in range(self.n_L):
            for s in range(self.n_S):
                for k in range(self.n_S):
                    model.addCons(u_values[l][s][k]*v[l][s]*k <= z)
        '''
        for l in range(self.n_L):
            for s in range(self.n_S):
                model.addCons(u_values_2[l][s]*v[l][s] <= z)

        #超過人数の合計を減らしつつ,シフトパターン希望順位での勤務を優先する,その際公平性も考慮する.
        model.setObjective(
            omega_3*phi_3*quicksum(quicksum(self.w[s][t]*v[l][s] for s in range(self.n_S)for l in range(self.n_L))-self.n_D[t] for t in range(self.n_T)) 
            + omega_4*phi_4*quicksum((u_values_2[l][s]* v[l][s] ) for s in range(self.n_S)  for l in range(self.n_L))
            +omega_5*phi_5*z,"minimize"
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
            self.ret[6] =  sum((self.w[s][t] * v_values[l][s] * self.h_N[l][t]) 
                               for l in range(self.n_L) for s in range(self.n_S) for t in range(self.n_T)) 
            print("勤務不可での勤務:",self.ret[6])
        
        else:
            print("Problem2 could not be solved to optimality")
            self.ret[1] = 0

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
