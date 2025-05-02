# ─────────────────────────────────────────────
# Makefile for CWT analysis workflow
# ─────────────────────────────────────────────

.PHONY: all define_problem plot_all plot_AC clean

# デフォルト実行ターゲット
all: plot_all

# 1) 問題定義ファイルの生成
my_problem.yaml:
	python define.py -o $@

define_problem: my_problem.yaml

# 2) 全被検者 (A, B, C) の解析プロット
plot_all: define_problem
	python cwt.py my_problem.yaml

# 3) 被検者 A と C のみ解析、色上限を 90% に
plot_AC: define_problem
	python cwt.py my_problem.yaml --subjects A C --clip-quantile 0.90

# 不要ファイルの削除
clean:
	rm -f my_problem.yaml
