from matsu import solve_program1
from matsu import solve_program2
from matsu import solve_program3
from matsu import solve_program4
from matsu import solve_program5
import numpy as np
import graph
import glob

def multiple_problem(printLog):
    cnt1_f=cnt1_s=0
    cnt2_s=0
    cnt3_f=cnt3_s=0
    cnt1_total=cnt2_total=cnt3_total=0
    over_labors=[[],[],[]]
    fulfill_preferences=[[],[],[]]
    files = glob.glob("./json/*.json")
    for file in files:
        ret=[]
        
        # 最適化プログラム実行
        append_flag=True
        if printLog:
            print(f"\n~~~~Results of Problem{file[15:-5]}~~~~")
        ret.append(solve_program4.solve(file,printLog))
        if ret[-1][0]==1:
            cnt1_f+=1
        if ret[-1][1]==1:
            cnt1_s+=1
        if ret[-1][0]==1 and ret[-1][1]==1:
            cnt1_total+=1
        else :
            append_flag=False

        if printLog:
            print("~~~~~~~~~~~~~~~~~~~~~~")
        #2個目のプログラム結果
        ret.append(solve_program5.solve(file,printLog))
        if ret[-1][1]==1:
            cnt2_s+=1
            cnt2_total+=1
        else :
            append_flag=False

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
            append_flag=False

        if append_flag is True:
            for i in range(3):
                over_labors[i].append(ret[i][2])
                fulfill_preferences[i].append(ret[i][3])
    print("plot data:",np.array(over_labors).shape[1])


    print(f'\nNumber of correct answers in the first stage:{cnt1_f}')
    print(f'Number of correct answers in the second stage:{cnt1_s}')
    print(f'Total number of correct answers:{cnt1_total}')

    print(f'Number of correct answers in the second stage:{cnt2_s}')
    print(f'Total number of correct answers:{cnt2_total}')

    print(f'Number of correct answers in the first stage:{cnt3_f}')
    print(f'Number of correct answers in the second stage:{cnt3_s}')
    print(f'Total number of correct answers:{cnt3_total}')

    #　条件可視化
    sdv=graph.ShiftDataVisualizer()
    sdv.show_scatter(over_labors,fulfill_preferences)
    


def single_problem(file_path,printLog):
    solve_program1.solve(file_path,printLog)
    print("~~~~~~~~~~~~~~~~~~~~~~")
    solve_program2.solve(file_path,printLog)
    print("~~~~~~~~~~~~~~~~~~~~~~")
    solve_program3.solve(file_path,printLog)

    #　条件可視化
    sdv=graph.ShiftDataVisualizer(file_path)
    sdv.show_graph()
    

def mediator(s_or_m,file_path,printLog):
    if s_or_m=='s':
        single_problem(file_path,printLog)
    elif s_or_m=='m':
        multiple_problem(printLog)
    else :
        print("You input is invalid.Please input 's' or 'm' at the first argument.")
    