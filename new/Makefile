# ─────────────────────────────────────────────
# Makefile for dynamic CWT analysis workflow
# ─────────────────────────────────────────────

.PHONY: all define_problem plot_all plot_power plot_phase plot_integrated clean

# Default target: full power scalogram for all subjects
all: plot_power

# Generate config file
my_problem.yaml:
	python define.py -o $@

define_problem: my_problem.yaml

# Plot all subjects power scalogram
plot_all: define_problem
	python cwt.py my_problem.yaml --mode power

# Plot power scalogram (default)
power: define_problem
	python cwt.py my_problem.yaml --mode power

# Plot phase
phase: define_problem
	python cwt.py my_problem.yaml --mode phase

# Plot integrated power
integrated: define_problem
	python cwt.py my_problem.yaml --mode integrated

# Customized subjects example (A and C only, 90% clip)
plot_AC: define_problem
	python cwt.py my_problem.yaml --subjects A C --clip-quantile 0.90 --mode power

# Clean up
clean:
	rm -f my_problem.yaml