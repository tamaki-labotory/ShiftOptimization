# ─────────────────────────────────────────────
# Makefile for dynamic CWT analysis workflow
# ─────────────────────────────────────────────

.PHONY: all define_problem plot_all plot_power plot_phase plot_integrated 

# Default target: full power scalogram for all subjects
all: power

# Generate config file
exam2.yaml:
	python define.py -o $@

define_problem: exam2.yaml



# Plot power scalogram (default)
power: define_problem
	python cwt.py exam2.yaml --mode power

# Plot phase
phase: define_problem
	python cwt.py exam2.yaml --mode phase

# Plot integrated power
integrated: define_problem
	python cwt.py exam2.yaml --mode integrated

plot_AC: define_problem
	python cwt.py exam2.yaml --subjects A C --clip-quantile 0.90 --mode power


# Plot situation
showData: define_problem
	python showData.py exam2.yaml