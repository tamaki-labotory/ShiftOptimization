import json
import numpy as np
from pulp import LpProblem, LpVariable, LpMinimize, LpMaximize, lpSum, PULP_CBC_CMD, value

class ShiftScheduler:
    def __init__(self, file_path, print_log=False):
        self.file_path = file_path
        self.print_log = print_log
        self.shift_data = self._load_data()
        self.n_S = len(self.shift_data["shift_patterns"])
        self.n_T = len(self.shift_data["shift_patterns"][0])
        self.n_L = len(self.shift_data["preferences"])
        self.n_D = self.shift_data["required_employees"]
        self.w = self.shift_data["shift_patterns"]
        self.h_P = self.shift_data["preferences"]
        self.h_N = self.shift_data["unavailable_slots"]
        self.ret=[0]*4

    def _load_data(self):
        with open(self.file_path, "r") as f:
            return json.load(f)

    def solve(self):
        raise NotImplementedError("Subclasses should implement the solve method.")

    def print_results(self, ret):
        if self.print_log:
            print(f"Step 1 Status: {'Success' if ret[0] == 1 else 'Failure'}")
            print(f"Step 2 Status: {'Success' if ret[1] == 1 else 'Failure'}")
            print(f"Overstaffing Hours: {ret[2]}")
            print(f"Employee Satisfaction: {ret[3]}")