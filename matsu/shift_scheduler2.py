"""
1段階目:各シフトパターンに割り振る人数枠を順次決定
2段階目:各従業員をどのシフトパターンに割り付けるか決定
という順でシフトを作成するプログラム
"""
import numpy as np
from pulp import LpProblem, LpVariable, LpMinimize,LpMaximize, lpSum, LpStatus, LpStatusOptimal,PULP_CBC_CMD, value
from program.matsu.shift_scheduler import ShiftScheduler


class ShiftScheduler2(ShiftScheduler):
    def solve(self):
        # 問題の定義
        # problem1 = LpProblem("Shift_Assignment", LpMinimize)
        problem2 = LpProblem("Shift_Assignment", LpMaximize)

        # 変数の設定
        x = [0]*self.n_S  # シフトパターンに割り当てる人数
        y = LpVariable.dicts("y", (range(self.n_L), range(self.n_S)), cat='Binary')  # 従業員がシフトパターンに割り当てられているか

        #################１段目#################
        #時間占有度計算
        alpha=[[0]*self.n_T for _ in range(self.n_S)]
        num_work_shifts=[0]*self.n_T
        for t in range(self.n_T):
            num_work_shifts[t]=sum(row[t] for row in self.w)
            for s in range(self.n_S):
                if self.w[s][t]==1:
                    alpha[s][t]=self.n_D[t]/num_work_shifts[t]
        
        #平均占有度計算
        beta= [0]*self.n_S
        for s in range(self.n_S):
            # beta[s]=sum(alpha[s])/sum(w[s])
            beta[s]=sum(self.w[s][t]*self.n_D[t] for t in range(self.n_T))

        #希望的適合度計算
        gamma=[[0]*self.n_S for _ in range(self.n_L)]
        M=1001001001 #十分大きな数
        for s in range(self.n_S):
            num_work_times=sum(self.w[s])
            for l in range(self.n_L):
                gamma[l][s]=sum(self.w[s][t]*(self.h_P[l][t]-M*self.h_N[l][t]) for t in range(self.n_T))/num_work_times

        #希望充足度
        delta=[0]*self.n_S
        for s in range(self.n_S):
            delta[s]=sum(max(0,gamma[l][s]) for l in range(self.n_L))/self.n_L

        #残りの必要人数
        remain=[v for v in self.n_D]

        #返り値
        #[1段階目成功可否,2段階目成功可否,超過人時,希望充足時]
        ret=[0]*4

        while 1:
            objective_function=[beta[i]+delta[i] for i in range(self.n_S)]
            best_value=max(objective_function)
            best_index=[]
            for s in range(self.n_S):
                if objective_function[s]==best_value:
                    best_index.append(s)
                    x[s]+=1
            for s in best_index:
                for t in range(self.n_T):
                    if self.w[s][t]==1:
                        remain[t]-=1

            # for t in range(self.n_T):
            #     for s in range(self.n_S):
            #         if w[s][t]==1:
            #             alpha[s][t]=remain[t]/num_work_shifts[t]
        
            #平均占有度更新
            for s in range(self.n_S):
                # beta[s]=sum(alpha[s])/sum(w[s])
                beta[s]=sum(self.w[s][t]*max(remain[t],0) for t in range(self.n_T))
        
            if all(b <= 0 for b in beta):
                break
        
        over_labors=0
        under_labors=0
        for t in range(self.n_T):
            tmp=sum(self.w[s][t]*x[s] for s in range(self.n_S))-self.n_D[t]
            if tmp>0:
                over_labors+=tmp
            if tmp<0:
                under_labors+=tmp
        
        if under_labors==0:
                ret[0]=1
        ret[2]=over_labors


        # #################２段目#################

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
        ret[1]=problem2.status
        ret[3]=value(problem2.objective)/self.n_L
