import random
from deap import base, creator, tools, algorithms
import numpy as np
import matplotlib.pyplot as plt
import sys
sys.path.append("/Users/matsumura/Desktop/修論/solver") 
import graph
from matplotlib.colors import ListedColormap, BoundaryNorm
from pulp import LpVariable, lpSum, value, LpProblem, LpMinimize,LpMaximize, PULP_CBC_CMD,LpStatusOptimal

# パラメータの定義
n_S = 5  # シフト数
n_T = 3  # 時間帯数
n_L = 4  # 従業員数
# ランダムなデータ
np.random.seed(0)
w = np.random.randint(1, 3, (n_S, n_T))      # 各シフトの従業員数
n_D = np.random.randint(5, 10, n_T)          # 各時間帯の必要人数
h_P = np.random.randint(0, 2, (n_L, n_T))    # 各従業員の希望
h_N = np.random.randint(0, 2, (n_L, n_T))    # 各従業員の希望外シフト

data = {
        "required_employees": n_D,
        "shift_patterns": w,
        "preferences": h_P,
        "unavailable_slots": h_N
    }

sdv=graph.ShiftDataVisualizer(None,data)
sdv.show_graph()

# 制約違反のペナルティ係数
penalty1 = 10.0
penalty2 = 5.0

# 遺伝的アルゴリズムのセットアップ
creator.create("FitnessMulti", base.Fitness, weights=(-1.0, -1.0))
creator.create("Individual", list, fitness=creator.FitnessMulti)
toolbox = base.Toolbox()
toolbox.register("attr_bool", random.randint, 0, 1)
toolbox.register("individual", tools.initRepeat, creator.Individual, toolbox.attr_bool, n_S)
toolbox.register("population", tools.initRepeat, list, toolbox.individual)

# 目的関数の定義
def objective(individual):
    # シフト変数 x を定義
    x = [LpVariable(f"x_{s}", cat="Binary") for s in range(n_S)]

    # 問題1: 超過人数の最小化
    problem1 = LpProblem("Minimize_OverLabors", LpMinimize)
    over_labors_cost = lpSum([lpSum([w[s][t] * individual[s] for s in range(n_S)]) - n_D[t] for t in range(n_T)])
    
    # ペナルティを追加
    penalty1_cost = penalty1 * lpSum([n_D[t] - lpSum(w[s][t] * individual[s] for s in range(n_S)) for t in range(n_T) if value(lpSum(w[s][t] * individual[s] for s in range(n_S))) < n_D[t]])
    problem1 += over_labors_cost + penalty1_cost

    # 解を求める
    problem1.solve(PULP_CBC_CMD(msg=False))
    
    # 問題2: 従業員の希望の最大化
    problem2 = LpProblem("Maximize_FulfillPreferences", LpMaximize)
    fulfill_preferences_cost = lpSum([lpSum([individual[s] * w[s][t] * h_P[l][t] for s in range(n_S)]) for t in range(n_T) for l in range(n_L)])
    
    # ペナルティを追加
    penalty2_cost = penalty2 * lpSum([lpSum(individual[s] * w[s][t] * h_N[l][t] for s in range(n_S)) for t in range(n_T) for l in range(n_L)])
    problem2 += fulfill_preferences_cost + penalty2_cost

    # 解を求める
    problem2.solve(PULP_CBC_CMD(msg=False))
    
    # 解が見つかったか確認し、それに応じて値を返す
    if problem1.status == LpStatusOptimal and value(problem1.objective) is not None:
        objective1 = value(problem1.objective)
    else:
        objective1 = float('inf')  # ペナルティとして非常に大きな値を設定
    
    if problem2.status == LpStatusOptimal and value(problem2.objective) is not None:
        objective2 = value(problem2.objective)
    else:
        objective2 = float('-inf')  # ペナルティとして非常に小さな値を設定

    return objective1, -objective2  # 最小化のため、希望充足度は符号を反転


# 評価関数を登録
toolbox.register("evaluate", objective)
toolbox.register("mate", tools.cxTwoPoint)
toolbox.register("mutate", tools.mutFlipBit, indpb=0.05)
toolbox.register("select", tools.selNSGA2)

# 遺伝的アルゴリズムの実行
def main():
    random.seed(0)
    population = toolbox.population(n=100)
    NGEN = 50  # 世代数
    MU = 50    # 選択する親の数
    LAMBDA = 100  # 子孫数
    CXPB, MUTPB = 0.7, 0.2  # 交叉と突然変異の確率

    # NSGA-IIで進化を繰り返す
    for gen in range(NGEN):
        offspring = algorithms.varOr(population, toolbox, lambda_=LAMBDA, cxpb=CXPB, mutpb=MUTPB)
        fits = map(toolbox.evaluate, offspring)
        
        for fit, ind in zip(fits, offspring):
            ind.fitness.values = fit
        population = toolbox.select(offspring, k=MU)
        
    return population

# 遺伝的アルゴリズムの結果を取得し、結果の評価
if __name__ == "__main__":
    final_population = main()
    for ind in final_population:
        print(f"Individual: {ind}, Objective Values: {ind.fitness.values}")
