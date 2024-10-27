import json

# JSONファイルのパス
file_path = "shift_data.json"

# JSONファイルからデータを読み込む
with open(file_path, "r") as f:
    shift_data = json.load(f)

# 読み込んだデータの表示
print("Required Employees per Time Slot:")
print(shift_data["required_employees"])

print("\nShift Patterns:")
for i, pattern in enumerate(shift_data["shift_patterns"]):
    print(f"Pattern {i+1}: {pattern}")

print("\nPreferences:")
for i, preference in enumerate(shift_data["preferences"]):
    print(f"Employee {i+1}: {preference}")

print("\nUnavailable Slots:")
for i, unavailable in enumerate(shift_data["unavailable_slots"]):
    print(f"Employee {i+1}: {unavailable}")

