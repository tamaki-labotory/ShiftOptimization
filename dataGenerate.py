import numpy as np
import json

# パラメータ設定
time_slots = 12
num_employees = 10


def generate_continuous_timezone():
    pattern = [0] * time_slots
    # ランダムに連続する時間の長さと開始位置を決定
    start = np.random.randint(0, time_slots - 4)  # 開始位置
    duration = np.random.randint(3, 8)  # 連続時間を3~8に設定
    for i in range(start, min(start + duration, time_slots)):
        pattern[i] = 1
    return pattern

def generate_unavailable_timezone(shift_preference):
    timezone = [0] * time_slots
    for i in range(len(timezone)):
        if shift_preference[i]==1:
            timezone[i]=0
        else :
            timezone[i]=int(np.random.choice([0,0,0,1]))
    return timezone

def generate_required_employees():
    required_employees = [0] * time_slots
    for i in range(time_slots):
        required_employees[i]=int(np.random.randint(1, 4))
    return required_employees


# 連続シフトパターン、希望勤務時間帯、勤務不可時間帯の生成
shift_patterns = [generate_continuous_timezone() for _ in range(num_employees)]
shift_preferences = [generate_continuous_timezone() for _ in range(num_employees)]
unavailable_slots = [generate_unavailable_timezone(shift_preferences[i]) for i in range(num_employees)]
required_employees_per_time_slot = generate_required_employees()

# 結果の出力
shift_data = {
    "required_employees": required_employees_per_time_slot,
    "shift_patterns": shift_patterns,
    "preferences": shift_preferences,
    "unavailable_slots": unavailable_slots
}

file_path = "shift_data.json"

# JSON形式で保存
with open(file_path, "w") as f:
    json.dump(shift_data, f, indent=4)

# shift_dataを保存するファイルパス
file_path = "shift_data.txt"

# テキスト形式で保存
with open(file_path, "w") as f:
    for key, value in shift_data.items():
        f.write(f"{key}:\n{value}\n\n")


