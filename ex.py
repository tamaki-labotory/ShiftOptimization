from pyscipopt import Model
# モデルの作成
model = Model("example")

# 変数の追加
x = model.addVar("x", vtype="C")
y = model.addVar("y", vtype="I")  # 整数変数

# 制約の追加
model.addCons(x + y >= 1)
model.addCons(2*x + y <= 3)

# 目的関数の設定
model.setObjective(x + y, "minimize")

# 問題を解く
model.optimize()

# 結果の出力
if model.getStatus() == "optimal":
    print("Optimal value:", model.getObjVal())
    print("x =", model.getVal(x))
    print("y =", model.getVal(y))
else:
    print("Problem could not be solved to optimality")