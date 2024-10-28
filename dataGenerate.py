import numpy as np
import json



def generate_continuous_timezone(time_slots):
    pattern = [0] * time_slots
    # ランダムに連続する時間の長さと開始位置を決定
    start = np.random.randint(0, time_slots - 4)  # 開始位置
    duration = np.random.randint(3, 8)  # 連続時間を3~8に設定
    for i in range(start, min(start + duration, time_slots)):
        pattern[i] = 1
    return pattern


def generate_shift_pattern(time_slots,num_shift_pattern):
    start_and_duration={}
    for i in range(num_shift_pattern):
        # ランダムに連続する時間の長さと開始位置を決定
        while 1:
            s=np.random.randint(0, time_slots - 4)
            d=np.random.randint(3, 8)
            if start_and_duration.get((s,d)) is not None:
                continue
            start_and_duration[(s,d)]=True  
            break

    shift_patterns=[]
    for sd,b in start_and_duration.items():
        pattern = [0] * time_slots
        for i in range(sd[0], min(sd[0] + sd[1] , time_slots)):
            pattern[i] = 1
        shift_patterns.append(pattern)
    
    checkFlag=True
    shift_patterns=np.array(shift_patterns)
    for i in range(time_slots):
        if sum(shift_patterns[:,i])==0: checkFlag=False

    if checkFlag is not True:
        shift_patterns=generate_shift_pattern(time_slots,num_shift_pattern)
    else :
        shift_patterns=shift_patterns.tolist()

    return shift_patterns


def generate_unavailable_timezone(shift_preference,time_slots):
    timezone = [0] * time_slots
    for i in range(len(timezone)):
        if shift_preference[i]==1:
            timezone[i]=0
        else :
            timezone[i]=int(np.random.choice([0,0,0,1]))
    return timezone

def generate_required_employees(time_slots):
    required_employees = [0] * time_slots
    for i in range(time_slots):
        required_employees[i]=int(np.random.randint(1, 10))
    return required_employees


def create_new_problem(file_path1,file_path2):
    # パラメータ設定
    time_slots = 12
    num_employees = np.random.randint(5, 20)
    num_shift_pattern = np.random.randint(6, 10)

    # 連続シフトパターン、希望勤務時間帯、勤務不可時間帯の生成
    shift_patterns = generate_shift_pattern(time_slots,num_shift_pattern)
    shift_preferences = [generate_continuous_timezone(time_slots) for _ in range(num_employees)]
    unavailable_slots = [generate_unavailable_timezone(shift_preferences[i],time_slots) for i in range(num_employees)]
    required_employees_per_time_slot = generate_required_employees(time_slots)

    # 結果の出力
    shift_data = {
        "required_employees": required_employees_per_time_slot,
        "shift_patterns": shift_patterns,
        "preferences": shift_preferences,
        "unavailable_slots": unavailable_slots
    }

    # JSON形式で保存
    with open(file_path1, "w") as f:
        json.dump(shift_data, f, indent=4)

    # テキスト形式で保存
    with open(file_path2, "w") as f:
        for key, value in shift_data.items():
            f.write(f"{key}:\n{value}\n\n")


for i in range(200):
    create_new_problem(f'json/shift_data{i+1}.json',f'txt/shift_data{i+1}.txt')

