import sys
import os
# プロジェクトのルートディレクトリをsys.pathに追加
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from matsu import shift_scheduler1
from matsu import shift_scheduler2
from matsu import shift_scheduler3
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
    files = glob.glob("/Users/matsumura/Desktop/修論/program/json/*.json")

    for file in files:
        ret=[]
        ShiftScheduler1=shift_scheduler1.ShiftScheduler1(file,printLog)
        ShiftScheduler2=shift_scheduler2.ShiftScheduler2(file,printLog)
        ShiftScheduler3=shift_scheduler3.ShiftScheduler3(file,printLog)
        ShiftScheduler1.solve()
        ShiftScheduler2.solve()
        ShiftScheduler3.solve()
        
        # 最適化プログラム実行
        append_flag=True
        if printLog:
            print(f"\n~~~~Results of Problem{file[50:-5]}~~~~")
    
        ret.append(ShiftScheduler1.ret)
        if ret[-1][0]==1:
            cnt1_f+=1
        if ret[-1][1]==1:
            cnt1_s+=1
        if ret[-1][0]==1 and ret[-1][1]==1:
            cnt1_total+=1
        else :
            append_flag=False

        if printLog:
            ShiftScheduler1.print_results()
            print("~~~~~~~~~~~~~~~~~~~~~~")

        #2個目のプログラム結果
        ret.append(ShiftScheduler2.ret)
        if ret[-1][1]==1:
            cnt2_s+=1
            cnt2_total+=1
        else :
            append_flag=False

        if printLog:
            ShiftScheduler2.print_results()
            print("~~~~~~~~~~~~~~~~~~~~~~")

        #3個目のプログラム結果
        ret.append(ShiftScheduler3.ret)
        if ret[-1][0]==1:
            cnt3_f+=1
        if ret[-1][1]==1:
            cnt3_s+=1
        if ret[-1][0]==1 and ret[-1][1]==1:
            cnt3_total+=1
        else :
            append_flag=False

        if printLog:
            ShiftScheduler3.print_results()

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
    ShiftScheduler1=shift_scheduler1.ShiftScheduler1(file_path,printLog)
    ShiftScheduler1.solve()
    ShiftScheduler1.print_results()
    print("~~~~~~~~~~~~~~~~~~~~~~")
    ShiftScheduler2=shift_scheduler2.ShiftScheduler2(file_path,printLog)
    ShiftScheduler2.solve()
    ShiftScheduler2.print_results()
    print("~~~~~~~~~~~~~~~~~~~~~~")
    ShiftScheduler3=shift_scheduler3.ShiftScheduler3(file_path,printLog)
    ShiftScheduler3.solve()
    ShiftScheduler3.print_results()

    #　条件可視化
    sdv=graph.ShiftDataVisualizer(file_path)
    # sdv.show_graph()
    sdv.show_assingn_state(ShiftScheduler3.ret[4])
    

def mediator(s_or_m,file_path,printLog):
    if s_or_m=='s':
        single_problem(file_path,printLog)
    elif s_or_m=='m':
        multiple_problem(printLog)
    else :
        print("You input is invalid.Please input 's' or 'm' at the first argument.")
    