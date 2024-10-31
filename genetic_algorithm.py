from __future__ import annotations

import json
from typing import Tuple, TypeVar, List, Dict
from random import choices, random, randrange, shuffle
from heapq import nlargest
from abc import ABC, abstractmethod
from copy import deepcopy
from datetime import datetime
from genetic_algorithm_module import Chromosome
from genetic_algorithm_module import GeneticAlgorithm
import numpy as np

M:int=1001001001

class Problem(Chromosome):

    def __init__(self, x: List[int],file_path : str) -> None:
        """
        遺伝的アルゴリズムにより、従業員側の目的関数を最適化する問題

        Parameters
        ----------
        x : List[int]
        シフト割り付けの初期値
        """
        self.x = x

        # JSONファイルからデータを読み込む
        with open(file_path, "r") as f:
            shift_data = json.load(f)

        # 定数の設定
        self.n_S = np.array(shift_data["shift_patterns"]).shape[0]
        self.n_T = np.array(shift_data["shift_patterns"]).shape[1]
        self.n_L = np.array(shift_data["preferences"]).shape[0]

        # 時間帯当たり必要人数
        self.n_D = shift_data["required_employees"]

        # 各シフトパターンごとで、勤務する時間帯でか（1: 必要、0: 不要）
        self.w = shift_data["shift_patterns"]

        # 従業員の勤務希望（1: 希望、0: 不希望）
        self.h_P = shift_data["preferences"]

        # 従業員の勤務不可能（1: 不可、0: ？）
        self.h_N = shift_data["unavailable_slots"]


    def get_fitness1(self) -> float:
        """
        各シフト割り付けに対し、目的関数1の評価値を計算

        """
        ret=0
        for l in range(self.n_L):
            if self.x[l]==-1:
                    continue
            for t in range(self.n_T):
                ret+=self.w[self.x[l]][t]*(self.h_P[l][t] - self.h_N[l][t]*M)

        return ret/70
    
    def get_fitness2(self) -> float:
        """
        各シフト割り付けに対し、目的関数2の評価値を計算

        """

        #各時間帯で働く人数を計算
        ret=[0]*self.n_T
        for l in range(self.n_L):
            if self.x[l]==-1:
                        continue  
            for t in range(self.n_T):
                ret[t]+=self.w[self.x[l]][t]
        for t in range(self.n_T):
            ret[t]-=self.n_D[t]

        #不足人数に対し、超過人数より割増しで低い評価をつける
        ret=[ret[t]+np.exp(-ret[t]*1000) for t in range(self.n_T)]

        return -sum(ret)/50

    @classmethod
    def make_random_instance(cls,file_path:str) -> Problem:
        """
        ランダムな初期値を与えた Problem クラスの
        インスタンスを生成する。

        Returns
        -------
        problem : Problem
            生成されたインスタンス
        """
        problem = Problem(x=[],file_path=file_path)
        x=[0]*problem.n_L
        for i in range(problem.n_L):
            x[i]=np.random.randint(-1,problem.n_S)
        problem.x=x

        return problem


    def mutate(self) -> None:
        """
        個体を（突然）変異させる（乱数に応じて、ある従業員に割り当てるシフトインデックスの値を
        1増減させる）。
        """
        value: int = choices([1, -1], k=1)[0]
        index: int = np.random.randint(0,self.n_L)
        
        self.x[index]=(self.x[index]+1+value)%(self.n_S+1)-1
        
        

    def exec_crossover(
            self: Problem, other: Problem
            ) -> List[Problem]:
        """
        引数に指定された別の個体を参照し交叉を実行する。

        Parameters
        ----------
        other : Problem
            交叉で利用する別の個体。

        Returns
        -------
        result_chromosomes : list of Problem
            交叉実行後に生成された2つの個体を格納したリスト。親となる
            個体それぞれから、xとyの値を半分ずつ受け継いだ個体となる。
        """
        child_1: Problem = deepcopy(self)
        child_2: Problem = deepcopy(other)

        indexes: List[int] = choices(np.linspace(0,self.n_S-1,self.n_S,dtype=int), k=np.random.randint(2,len(child_1.x)//2))
        for index in indexes:
            tmp=child_1.x[index]
            child_1.x[index] = other.x[index]
            child_2.x[index] = tmp
            result_chromosomes: List[Problem] = [
                child_1, child_2,
            ]
        # print(f"child1:{child_1.x},child2:{child_2.x}")
        return result_chromosomes

    def __str__(self) -> str:
        """
        個体情報の文字列を返却する。

        Returns
        -------
        info : str
            個体情報の文字列。
        """
        #超過人数・不足人数計算
        over_labors=under_labors=0
        workers=[0]*self.n_T
        for l in range(self.n_L):
            if self.x[l]==-1:
                        continue  
            for t in range(self.n_T):
                workers[t]+=self.w[self.x[l]][t]
        for t in range(self.n_T):
            if workers[t]-self.n_D[t]<0:
                under_labors-=workers[t]-self.n_D[t]
            else:
                over_labors+=workers[t]-self.n_D[t]

        shifts: List[int] = [self.x[i] for i in range(self.n_L)]
        for i in range(len(shifts)):
             if shifts[i]!=-1:
                  shifts[i]+=1
                  
        fitness: List[float] = [self.get_fitness1(),self.get_fitness2()]

        info: str = f'シフト割り付け:{shifts}, 超過人数:{over_labors}, 不足人数:{under_labors}, 従業員満足度:{fitness[0]*70/self.n_L}, fitness:{fitness}'
        return info
    


if __name__ == '__main__':

    instances1: List[Problem] = [Problem.make_random_instance("/Users/matsumura/Desktop/修論/solver/json/shift_data132.json") for _ in range(200)]
    instances2: List[Problem] = [Problem.make_random_instance("/Users/matsumura/Desktop/修論/solver/json/shift_data132.json") for _ in range(200)]
    ga: GeneticAlgorithm = GeneticAlgorithm(
        initial_population1=instances1,
        initial_population2=instances2,
        threshold=100,
        max_generations=3000,
        mutation_probability=0.5,
        crossover_probability=0.5,
        selection_type=GeneticAlgorithm.SELECTION_TYPE_TOURNAMENT)
    _ = ga.run_algorithm()



# ~~~~Results of Problema/Desktop/修論/solver/json/shift_data132~~~~
# 超過人数: 23.0
# 各シフトパターンの割り当て人数:[0, 0, 3, 6, 0, 0, 3, 0, 0]
# ２階目の従業員の割り当て:[-1, 3, 4, 4, 7, 7, 4, 3, 4, 4, 7, 3, -1, 4, -1, -1]
# 従業員満足度: 2.9375
# ~~~~~~~~~~~~~~~~~~~~~~
# 超過人数: 46.0
# 各シフトパターンの割り当て人数:[0, 0, 3, 3, 4, 0, 6, 0, 0]
# The optimal solution for the second step was not found.
# ~~~~~~~~~~~~~~~~~~~~~~
# 超過人数: 23.0
# 各シフトパターンの割り当て人数:[0, 0, 3, 6, 0, 0, 3, 0, 0]
# ２階目の従業員の割り当て:[-1, 3, 4, 4, 7, 7, 4, 3, 4, 4, 7, 3, -1, 4, -1, -1]
# 従業員満足度: 2.9375