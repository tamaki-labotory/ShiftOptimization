"""
各種ソルバーを実行するメインプログラム
"""

import graph
import glob
import solve_program1
import solve_program2
import solve_program3

def multiple_problem(printLog):
    cnt1_f=cnt1_s=0
    cnt2_s=0
    cnt3_f=cnt3_s=0
    cnt1_total=cnt2_total=cnt3_total=0
    files = glob.glob("json/*.json")
    for file in files:
        # 最適化プログラム実行
        if printLog:
            print(f"\n~~~~Results of Problem{file[15:-5]}~~~~")
        result1,result2=solve_program1.solve(file,printLog)
        if result1==1:
            cnt1_f+=1
        if result2==1:
            cnt1_s+=1
        if result1==1 and result2==1:
            cnt1_total+=1

        print("~~~~~~~~~~~~~~~~~~~~~~")
        result2=solve_program2.solve(file,printLog)
        if result2==1:
            cnt2_s+=1
            cnt2_total+=1

        print("~~~~~~~~~~~~~~~~~~~~~~")
        result1,result2=solve_program3.solve(file,printLog)
        if result1==1:
            cnt3_f+=1
        if result2==1:
            cnt3_s+=1
        if result1==1 and result2==1:
            cnt3_total+=1

    print(f'\nNumber of correct answers in the first stage:{cnt1_f}')
    print(f'Number of correct answers in the second stage:{cnt1_s}')
    print(f'Total number of correct answers:{cnt1_total}')

    print(f'Number of correct answers in the second stage:{cnt2_s}')
    print(f'Total number of correct answers:{cnt2_total}')

    print(f'Number of correct answers in the first stage:{cnt3_f}')
    print(f'Number of correct answers in the second stage:{cnt3_s}')
    print(f'Total number of correct answers:{cnt3_total}')


def single_problem(file_path,printLog):
    solve_program1.solve(file_path,printLog)
    print("~~~~~~~~~~~~~~~~~~~~~~")
    solve_program2.solve(file_path,printLog)
    print("~~~~~~~~~~~~~~~~~~~~~~")
    solve_program3.solve(file_path,printLog)

    #　条件可視化
    graph.show_graph(file_path)
    
    

# メインプログラムとして実行された場合にmain()を呼び出す
if __name__ == "__main__":
    # single_problem("json/shift_data85.json",True)
    multiple_problem(True)