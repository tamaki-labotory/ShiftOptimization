"""
テストデータを作成するプログラム
"""

import random
import numpy as np
import json



###############################################
##シフトセット作成
###############################################
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

#改訂版・シフトセット1(3交代制)
def generate_shift_pattern_1(time_slots,num_shift_pattern):
    start_and_duration={}
    for i in range(3):
        while 1:
                # 8時間勤務の交代制
                s = i*4
                d = 4
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
        shift_patterns=generate_shift_pattern_1(time_slots,num_shift_pattern)
    else :
        shift_patterns=shift_patterns.tolist()

    return shift_patterns


#改訂版・シフトセット2(シフトパターン数の少ない非交代制)
def generate_shift_pattern_2(time_slots,num_shift_pattern):
    start_and_duration={}
    #8時間勤務を二時間帯ずつずらして勤務
    for i in range(6):
        while 1:
            s = i*2
            d = 4
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
        shift_patterns=generate_shift_pattern_2(time_slots,num_shift_pattern)
    else :
        shift_patterns=shift_patterns.tolist()

    return shift_patterns

#改訂版・シフトセット3(シフトパターン数の多い非交代制)
def generate_shift_pattern_3(time_slots,num_shift_pattern):
    start_and_duration={}
    #6時間勤務を二時間帯ずつずらして勤務
    for i in range(6):
        while 1:
            s = i*2
            d = 3
            if start_and_duration.get((s,d)) is not None:
                    continue
            start_and_duration[(s,d)]=True
            break
    
    #8時間勤務を3時間帯ずつずらして勤務
    for i in range(4):
        while 1:
            s = i*3
            d = 4
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
        shift_patterns=generate_shift_pattern_3(time_slots,num_shift_pattern)
    else :
        shift_patterns=shift_patterns.tolist()

    return shift_patterns


#改訂版・シフトセット4(連続勤務時間制約をもつシフトパターンレス・シフトスケジューリング)
def generate_shift_pattern_4(time_slots,num_shift_pattern):
    start_and_duration={}
    for i in range(time_slots):
        # 開始時刻を単位時間ずつずらして時間帯数文作る
        #連続時間4~6時間を対象に行う
        for j in range(3,5,1):
            while 1:
                s = i
                d = j
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
        shift_patterns=generate_shift_pattern_4(time_slots,num_shift_pattern)
    else :
        shift_patterns=shift_patterns.tolist()

    return shift_patterns

'''
#コンビニバイトのシフトセットを参考に作成する
def generate_shift_pattern_1(time_slots,num_shift_pattern):
    start_and_duration={}
    for i in range(6):
        while 1:
                # 4時間勤務の交代制
                s = i*2
                d = 2
                if start_and_duration.get((s,d)) is not None:
                    continue
                start_and_duration[(s,d)]=True
                break
   
    for i in range(3):
        while 1:
                # 8時間勤務の交代制
                s = i*4
                d = 4
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
        shift_patterns=generate_shift_pattern_1(time_slots,num_shift_pattern)
    else :
        shift_patterns=shift_patterns.tolist()

    return shift_patterns
'''
'''
#飲食バイトのシフトセットを参考に作成する
def generate_shift_pattern_2(time_slots,num_shift_pattern):
    start_and_duration={}
    #6時間勤務を一時間帯ずつずらして勤務
    for i in range(time_slots):
        while 1:
            s = i
            d = 3
            if start_and_duration.get((s,d)) is not None:
                    continue
            start_and_duration[(s,d)]=True
            break
    #8時間勤務の三交代制
    for i in range(3):
        while 1:
            s = i*4
            d = 4
            if start_and_duration.get((s,d)) is not None:
                continue
            start_and_duration[(s,d)] = True
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
        shift_patterns=generate_shift_pattern_2(time_slots,num_shift_pattern)
    else :
        shift_patterns=shift_patterns.tolist()

    return shift_patterns
'''

###############################################

###############################################
##勤務希望・不可時間帯作成
###############################################
def generate_continuous_timezone(time_slots):
    pattern = [0] * time_slots
    # ランダムに連続する時間の長さと開始位置を決定
    start = np.random.randint(0, time_slots - 4)  # 開始位置
    duration = np.random.randint(3, 8)  # 連続時間を3~8に設定
    for i in range(start, start + duration):
        pattern[(i)%time_slots] = 1
    return pattern

def generate_unavailable_timezone(shift_preference,time_slots):
    timezone = [0] * time_slots
    for i in range(len(timezone)):
        if shift_preference[i]==1:
            timezone[i]=0
        else :
            timezone[i]=int(np.random.choice([0,0,0,1]))
    return timezone


##従業員の半分が日勤希望,半分が夜勤希望,勤務不可は他の時間から3時間をランダムに
def generate_prefere_timezone_1(num_employees,i,time_slots):
    pattern = [0] * time_slots
    # ランダムに連続する時間の長さと開始位置を決定
    duration = 6  # 連続時間を6
    if i <= (num_employees/2):  #半分は日勤希望
        start = 0
    else:  #半分は夜勤希望
        start = 6
    for i in range(start, start + duration):
        pattern[(i)%time_slots] = 1
    return pattern

def generate_unavailable_timezone_1(num_employees,shift_preferences,time_slots,i):
    timezone = [0] * time_slots
    
    np.random.seed(100+i)
    start = np.random.randint(0,time_slots)
    duration = 3
    for j in range(start,start+duration):
        if shift_preferences[j%time_slots] == 1:
            timezone[(j+6)%time_slots]=1
        else :
            timezone[(j)%time_slots] = 1
    return timezone

##従業員の1/3が日勤希望(1~4),1/3が準夜勤希望(4~8),1/3が夜勤希望(9~12),勤務不可は他の時間からランダムに4時間帯
def generate_prefere_timezone_2(num_employees,i,time_slots):
    pattern = [0] * time_slots
    duration = 4
    if i <= (num_employees/3):
        start = 0
    elif i<= (num_employees*2/3):
        start = 4
    else:
        start = 8
    for i in range(start, start + duration):
        pattern[(i)%time_slots] = 1
    return pattern
        
def generate_unavailable_timezone_2(num_employees,shift_preferences,time_slots,i):
    timezone = [0] * time_slots
    np.random.seed(200+i)
    start = np.random.randint(0,time_slots)
    duration = 3
    for j in range(start,start+duration):
        if shift_preferences[j%time_slots] == 1:
            timezone[(j+4)%time_slots]=1
        else :
            timezone[(j)%time_slots] = 1
    return timezone


##勤務希望が4時間帯の規則的バラバラ,勤務不可は勤務希望以外の時間帯からランダムに4時間帯
def generate_prefere_timezone_3(num_employees,i,time_slots):
    pattern = [0]*time_slots
    duration = 4
    start = i%time_slots
    for i in range(start, start + duration):
        pattern[(i)%time_slots] = 1
    return pattern

def generate_unavailable_timezone_3(num_employees,shift_preferences,time_slots,i):
    timezone = [0] * time_slots
    
    np.random.seed(300+i)
    start = np.random.randint(0,time_slots)
    duration = 3
    for j in range(start,start+duration):
        if shift_preferences[j%time_slots] == 1:
            timezone[(j+4)%time_slots]=1
        else :
            timezone[(j)%time_slots] = 1
    return timezone


    

###############################################

###############################################
##必要人数作成
###############################################

##ランダムシフト
def generate_required_employees(time_slots):
    required_employees = [0] * time_slots
    for i in range(time_slots):
        required_employees[i]=int(np.random.randint(2, 4))
    return required_employees

#改訂版・必要人数パターン1(全時間帯5人)
def generate_required_employees_1(time_slots):
    required_employees = [0] * time_slots
    for i in range(12):
        required_employees[i] = 5
    return required_employees

#改訂版・必要人数パターン2(日勤と準夜勤と夜勤)
def generate_required_employees_2(time_slots):
    required_employees = [0] * time_slots
    #夜勤
    for i in range(4):
        required_employees[i] = 2
    #日勤
    for i in range(4,8):
        required_employees[i] = 9
    #準夜勤
    for i in range(8,12):
        required_employees[i] = 4
    return required_employees

#改訂版・必要人数パターン3(特定の時間帯に必要人数が集中)
def generate_required_employees_3(time_slots):
    required_employees=[0]*time_slots
    required_employees[0] = 3
    required_employees[1] = 2
    required_employees[2] = 2
    required_employees[3] = 3
    required_employees[4] = 3
    required_employees[5] = 3
    required_employees[6] = 8
    required_employees[7] = 10
    required_employees[8] = 5
    required_employees[9] = 10
    required_employees[10] = 8
    required_employees[11] = 3
    return required_employees



'''
##シフトセット1 計42
def generate_required_employees_1(time_slots):
    required_employees = [0] * time_slots
    for i in range(6):
        required_employees[i] = 5
    for i in range(6,12):
        required_employees[i] = 2
    return required_employees

##シフトセット2 計42
def generate_required_employees_2(time_slots):
    required_employees = [0] * time_slots
    for i in range(3):
        required_employees[i] = 5
    required_employees[3] = 4
    required_employees[4] = 2
    required_employees[5] = 4
    required_employees[6] = 5
    required_employees[7] = 4
    required_employees[8] = 3
    required_employees[9] = 2
    required_employees[10] = 1
    required_employees[11] = 2
    return required_employees

##シフトセット3 計42
def generate_required_employees_3(time_slots):
    required_employees = [0] * time_slots
    required_employees[0] = 5
    required_employees[1] = 2
    required_employees[2] = 5
    required_employees[3] = 5
    required_employees[4] = 2
    required_employees[5] = 4
    required_employees[6] = 5
    required_employees[7] = 4
    required_employees[8] = 3
    required_employees[9] = 2
    required_employees[10] = 3
    required_employees[11] = 2
    return required_employees

'''


def create_new_problem(index):
    # パラメータ設定
    time_slots = 12
    #num_employees = np.random.randint(15, 20)
    num_employees = 46
    num_shift_pattern = np.random.randint(6, 10)

    # 連続シフトパターン、希望勤務時間帯、勤務不可時間帯の生成
    shift_patterns = generate_shift_pattern_3(time_slots,num_shift_pattern)
    shift_preferences = [generate_prefere_timezone_2(num_employees,i,time_slots) for i in range(num_employees)]
    unavailable_slots = [generate_unavailable_timezone_2(num_employees,shift_preferences[i],time_slots,i) for i in range(num_employees)]
    required_employees_per_time_slot = generate_required_employees_3(time_slots)

# JSON保存
    with open(f"json/shift_patterns_{index}.json", "w") as f:  
        json.dump({"shift_patterns": shift_patterns}, f, indent=4)

    with open(f"json/preferences_and_unavailable_slots_{index}.json", "w") as f:
        json.dump(
            {"preferences": shift_preferences, "unavailable_slots": unavailable_slots},
            f,
            indent=4
        )

    with open(f"json/required_employees_{index}.json", "w") as f:
        json.dump({"required_employees": required_employees_per_time_slot}, f, indent=4)

    # TXT保存
    with open(f"txt/shift_patterns_{index}.txt", "w") as f:
        f.write(f"shift_patterns:\n{shift_patterns}\n")

    with open(f"txt/preferences_and_unavailable_slots_{index}.txt", "w") as f:
        f.write(f"preferences:\n{shift_preferences}\n")
        f.write(f"unavailable_slots:\n{unavailable_slots}\n")

    with open(f"txt/required_employees_{index}.txt", "w") as f:
        f.write(f"required_employees:\n{required_employees_per_time_slot}\n")

for i in range(1):
    create_new_problem(i + 1)

'''    
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
'''
