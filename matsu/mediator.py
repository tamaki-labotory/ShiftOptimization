import sys

# passの設定 (pip showで出てきた、LocationのPASSを以下に設定)
sys.path.append('/Users/hymac/mypy/lib/python3.12/site-packages')
from matsu import solve_program1
from matsu import solve_program2
from matsu import solve_program3
from matsu import solve_program4
from matsu import solve_program5
from matsu import solve_program6
from matsu import solve_program7
from matsu import solve_program8
from matsu import solve_program9
import numpy as np
import graph
import glob

def multiple_problem(printLog):
    
    cnt1_f=cnt1_s=0
    cnt2_s=0
    cnt3_f=cnt2_f=cnt3_s=0
    cnt1_total=cnt2_total=cnt3_total=0
    cnt1_overlabors=cnt2_overlabors=cnt3_overlabors=0
    cnt1_satisfied=cnt2_satisfied=cnt3_satisfied=0
    cnt1_time=cnt2_time=cnt3_time=0

    over_labors=[[],[],[]]
    fulfill_preferences=[[],[],[]]
    time=[[],[],[]]
    files = glob.glob("./json/*.json")
    data_count = 0
    for file in files:
        ret=[]
        data_count+=1
        # 最適化プログラム実行
        append_flag=True
        if printLog:
            print(f"\n~~~~Results of Problem{file[15:-5]}~~~~")

        #1個目のプログラム結果
        ret.append(solve_program7.solve(file,printLog))
        if ret[-1][0]==1:
            cnt1_f+=1
        if ret[-1][1]==1:
            cnt1_s+=1
        if ret[-1][0]==1 and ret[-1][1]==1:
            cnt1_total+=1
        else :
            #append_flag=False
            append_flag = True

        if printLog:
            print("~~~~~~~~~~~~~~~~~~~~~~")
        #2個目のプログラム結果
        ret.append(solve_program8.solve(file,printLog))
        if ret[-1][0]==1:
            cnt2_f+=1
        if ret[-1][1]==1:
            cnt2_s+=1
        if ret[-1][0]==1 and ret[-1][1]==1:
            cnt2_total+=1
            
        else :
            #append_flag=False
            append_flag = True

        if printLog:
            print("~~~~~~~~~~~~~~~~~~~~~~")
        #3個目のプログラム結果
        ret.append(solve_program6.solve(file,printLog))
        if ret[-1][0]==1:
            cnt3_f+=1
        if ret[-1][1]==1:
            cnt3_s+=1
        if ret[-1][0]==1 and ret[-1][1]==1:
            cnt3_total+=1
            
        else :
            #append_flag=False
            append_flag = True

        if append_flag is True:
            for i in range(3):
                over_labors[i].append(ret[i][2])
                fulfill_preferences[i].append(ret[i][3])
                time[i].append(ret[i][4])
                if i == 0:
                    cnt1_overlabors+=ret[i][2]
                    cnt1_satisfied+=ret[i][3]
                    cnt1_time+=ret[i][4]
                if i == 1:
                    cnt2_overlabors+=ret[i][2]
                    cnt2_satisfied+=ret[i][3]
                    cnt2_time+=ret[i][4]
                if i == 2:
                    cnt3_overlabors+=ret[i][2]
                    cnt3_satisfied+=ret[i][3]
                    cnt3_time+=ret[i][4]
    print("plot data:",np.array(over_labors).shape[1])


    print(f'\nNumber of correct answers in the first stage:{cnt1_f}')
    print(f'Number of correct answers in the second stage:{cnt1_s}')
    print(f'Total number of correct answers:{cnt1_total}')
    print(f'Average number of overlabors:{cnt1_overlabors/data_count}')
    print(f'Average number of satisfied per number of labors:{cnt1_satisfied/data_count}')
    print(f'Average number of time:{cnt1_time/data_count}')

    print(f'\nNumber of correct answers in the first stage:{cnt2_f}')
    print(f'Number of correct answers in the second stage:{cnt2_s}')
    print(f'Total number of correct answers:{cnt2_total}')
    print(f'Average number of overlabors:{cnt2_overlabors/data_count}')
    print(f'Average number of satisfied per number of labors:{cnt2_satisfied/data_count}')
    print(f'Average number of time:{cnt2_time/data_count}')

    print(f'\nNumber of correct answers in the first stage:{cnt3_f}')
    print(f'Number of correct answers in the second stage:{cnt3_s}')
    print(f'Total number of correct answers:{cnt3_total}')
    print(f'Average number of overlabors:{cnt3_overlabors/data_count}')
    print(f'Average number of satisfied per number of labors:{cnt3_satisfied/data_count}')
    print(f'Average number of time:{cnt3_time/data_count}')

    graph.show_scatter(over_labors,fulfill_preferences)
    

def multiple_problem2(printLog):
    # 各プログラムの結果を保持するカウンターを初期化
    counts = {
        "f": [0] * 8,  # 一段階目成功数
        "s": [0] * 8,  # 二段階目成功数
        "total": [0] * 8,  # 全体成功数
        "overlabors": [0] * 8,  # 超過人数合計
        "satisfied": [0] * 8,  # 満足度合計
        "time": [0] * 8  # 実行時間合計
    }
    
    # データの記録用
    over_labors = [[] for _ in range(8)]
    fulfill_preferences = [[] for _ in range(8)]
    time = [[] for _ in range(8)]

    # JSON ファイルの取得
    files = glob.glob("./json/*.json")
    data_count = 0

    for file in files:
        ret = []
        data_count += 1
        append_flag = True  # 初期化

        if printLog:
            print(f"\n~~~~Results of Problem {file[15:-5]}~~~~")

        # 8つのプログラムを順に実行
        for i, solver in enumerate([
            solve_program1.solve,
            solve_program2.solve,
            solve_program3.solve,
            solve_program4.solve,
            solve_program5.solve,
            solve_program6.solve,
            solve_program7.solve,
            solve_program8.solve
        ]):
            # プログラムの結果を取得
            result = solver(file, printLog)
            ret.append(result)

            if result[0] == 1:
                counts["f"][i] += 1
            if result[1] == 1:
                counts["s"][i] += 1
            if result[0] == 1 and result[1] == 1:
                counts["total"][i] += 1
            else:
                # 超過人数や満足度の集計は成功したケースのみ対象
                append_flag = True

            # 成功時の記録
            if append_flag:
                over_labors[i].append(result[2])
                fulfill_preferences[i].append(result[3])
                time[i].append(result[4])
                counts["overlabors"][i] += result[2]
                counts["satisfied"][i] += result[3]
                counts["time"][i] += result[4]

    # 各プログラムの集計結果を表示
    for i in range(8):
        print(f"\nResults for Program {i+1}:")
        print(f"  - Number of correct answers in the first stage: {counts['f'][i]}")
        print(f"  - Number of correct answers in the second stage: {counts['s'][i]}")
        print(f"  - Total number of correct answers: {counts['total'][i]}")
        print(f"  - Average number of overlabors: {counts['overlabors'][i] / data_count}")
        print(f"  - Average number of satisfied per number of labors: {counts['satisfied'][i] / data_count}")
        print(f"  - Average execution time: {counts['time'][i] / data_count} ms")

    # 結果のプロット
    graph.show_scatter(over_labors, fulfill_preferences)

def single_problem(file_path,printLog):
    solve_program7.solve(file_path,printLog)
    print("~~~~~~~~~~~~~~~~~~~~~~")
    solve_program2.solve(file_path,printLog)
    print("~~~~~~~~~~~~~~~~~~~~~~")
    solve_program1.solve(file_path,printLog)

    #　条件可視化
    #graph.show_graph(file_path)
    graph.show_graph(file_path)
    

def mediator(s_or_m,file_path,printLog):
    if s_or_m=='s':
        single_problem(file_path,printLog)
    elif s_or_m=='m':
        multiple_problem(printLog)
    elif s_or_m == 'n':
        multiple_problem2(printLog)
    
    else :
        print("You input is invalid.Please input 's' or 'm' at the first argument.")
    