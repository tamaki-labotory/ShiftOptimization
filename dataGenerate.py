"""
例1を作成するプログラム
"""
import sys

# passの設定 (pip showで出てきた、LocationのPASSを以下に設定)
sys.path.append('/Users/hymac/mypy/lib/python3.12/site-packages')
import numpy as np
import json




#重なり時間帯のないシンプルな交代制シフトを想定した勤務時間を1にした配列を出力(num_shift_patternにはシフトパターン数が,num_of_shiftにはシフトパターン番号が与えられる)
def generate_continuous_timezone_2(time_slots,num_shift_pattern,num_of_shift):
    pattern = [0]*time_slots
    #連続時間の開始位置を決定
    start = (time_slots/num_shift_pattern) * num_of_shift
    #連続時間の長さを決定
    duration = time_slots/num_shift_pattern

    for i in range(start,start+duration):
        pattern[(i)%time_slots] = 1
    return pattern

'''
#ランダムにシフトパターンを生成
def generate_shift_pattern(time_slots,num_shift_pattern):
    start_and_duration={}
    for i in range(num_shift_pattern):
        # ランダムに連続する時間の長さと開始位置を決定
        while 1:
            s=np.random.randint(0, time_slots - 4)
            d=np.random.randint(4, 7)
            if start_and_duration.get((s,d)) is not None:
                continue
            start_and_duration[(s,d)]=True  
            break

    shift_patterns=[]
    for sd,b in start_and_duration.items():
        pattern = [0] * time_slots
        for i in range(sd[0], sd[0] + sd[1] ):
            pattern[(i)%time_slots] = 1
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
'''

##交代制のシフトパターンを作成
def generate_shift_pattern_2(time_slots,num_shift_pattern):
    shift_patterns=[]
    for i in range(num_shift_pattern):
        s = (time_slots/num_shift_pattern) * i
        s = int(s)
        d = time_slots/num_shift_pattern
        d = int(d)
        pattern = [0] * time_slots
        for j in range(s,s+d):
            pattern[(j)%time_slots] = 1
        shift_patterns.append(pattern)

    
    checkFlag=True
    shift_patterns=np.array(shift_patterns)
    '''
    for i in range(time_slots):
        if sum(shift_patterns[:,i])==0: checkFlag=False
    '''


    if checkFlag is not True:
        shift_patterns=generate_shift_pattern_2(time_slots,num_shift_pattern)
    else :
        shift_patterns=shift_patterns.tolist()

    return shift_patterns

##非交代制のシフトパターンを作成
def generate_shift_pattern_3(time_slots,num_shift_pattern):
    shift_patterns=[]
    for i in range(num_shift_pattern):
        s = (time_slots/num_shift_pattern) * i
        s = int(s)
        d = (time_slots/num_shift_pattern) + 2
        d = int(d)
        pattern = [0] * time_slots
        for j in range(s,s+d):
            pattern[(j)%time_slots] = 1
        shift_patterns.append(pattern)

    
    checkFlag=True
    shift_patterns=np.array(shift_patterns)
    '''
    for i in range(time_slots):
        if sum(shift_patterns[:,i])==0: checkFlag=False
    '''


    if checkFlag is not True:
        shift_patterns=generate_shift_pattern_3(time_slots,num_shift_pattern)
    else :
        shift_patterns=shift_patterns.tolist()

    return shift_patterns
'''
#勤務不可時間の作成
def generate_unavailable_timezone(shift_preference,time_slots):
    timezone = [0] * time_slots
    for i in range(len(timezone)):
        if shift_preference[i]==1:
            timezone[i]=0
        else :
            timezone[i]=int(np.random.choice([0,0,0,1]))
    return timezone
'''

#ランダムな長さの連続時間を1にした配列を出力(勤務希望作成に使用)
def generate_hope_timezone(time_slots):
    pattern = [0] * time_slots
    # ランダムに連続する時間の長さと開始位置を決定
    start = np.random.randint(0, time_slots)  # 開始位置
    duration = 2  # 連続時間を3~6に設定
    
    for i in range(start, start + duration):
        pattern[(i)%time_slots] = 1
    return pattern

#勤務不可時間の作成
def generate_unable_timezone(shift_preference,time_slots):
    pattern = [0]*time_slots
    #ランダムに連続する時間の長さと開始位置を決定
    start = np.random.randint(0, time_slots)  # 開始位置
    duration = 2  # 連続時間を3~6に設定
    for i in range(start, start + duration):
        if shift_preference[i%time_slots] == 1:
            pattern[(i+2)%time_slots] = 1
        else:
            pattern[(i)%time_slots] = 1
    return pattern


#時間帯あたり必要人数の作成
def generate_required_employees(time_slots):
    required_employees = [0] * time_slots
    for i in range(time_slots):
        if 0<=i<4:
            required_employees[i] = 8
        elif 4<=i<8:
            required_employees[i] = 3
        elif 8 <=i<12:
            required_employees[i] = 2
    return required_employees


def create_base_problem(file_path1,file_path2):
    # パラメータ設定
    time_slots = 12
    num_employees = 25
    #num_shift_pattern = np.random.randint(6, 10)
    num_shift_pattern = 4

    # 連続シフトパターン、希望勤務時間帯、勤務不可時間帯の生成
    shift_patterns = generate_shift_pattern_3(time_slots,num_shift_pattern)
    shift_preferences = [generate_hope_timezone(time_slots) for _ in range(num_employees)]
    unavailable_slots = [generate_unable_timezone(shift_preferences[i],time_slots) for i in range(num_employees)]
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
    
    return required_employees_per_time_slot,shift_patterns,shift_preferences,unavailable_slots

#dataの読み込み
def load_base_data(file_path):
    with open(file_path,"r") as f:
        data = json.load(f)
    return data

#basedataからの修正データ作成
def modify_problem(num,file_path1,file_path2):
    base_data = load_base_data("json/base_data.json")
    required_employees = base_data["required_employees"]
    shift_patterns = base_data["shift_patterns"]
    preferences = base_data["preferences"]
    unavailable_slots = base_data["unavailable_slots"]

    new_preferences = preferences
    new_unavailable_slots = unavailable_slots
    for i in range(25):
        if i == num:
            new_preferences[i] = [0 for _ in range(12)]
            new_unavailable_slots[i] = [1 for _ in range(12)]

    new_data = {
        "required_employees": required_employees,
        "shift_patterns": shift_patterns,
        "preferences": new_preferences,
        "unavailable_slots": new_unavailable_slots
    }    

    # JSON形式で保存
    with open(file_path1, "w") as f:
        json.dump(new_data, f, indent=4)

    # テキスト形式で保存
    with open(file_path2, "w") as f:
        for key, value in new_data.items():
            f.write(f"{key}:\n{value}\n\n")





create_base_problem(f'json/base_data.json',f'txt/base_data.txt')

for i in range(25):
    modify_problem(i,f'json/shift_data{i+1}.json',f'txt/shift_data{i+1}.txt')
