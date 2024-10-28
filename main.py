"""
各種ソルバーを実行するメインプログラム
"""

import graph
import glob
import solve_program1
import solve_program2

def multiple_problem(printLog):
    cnt_f=0
    cnt_s=0
    cnt_total=0
    files = glob.glob("json/*.json")
    for file in files:
        # 最適化プログラム実行
        if printLog:
            print(f"\n~~~~Results of Problem{file[15:-5]}~~~~")
        result1,result2=solve_program2.solve(file,printLog)
        if result1==1:
            cnt_f+=1
        if result2==1:
            cnt_s+=1
        if result1==1 and result2==1:
            cnt_total+=1
    print(f'\nNumber of correct answers in the first stage:{cnt_f}')
    print(f'Number of correct answers in the second stage:{cnt_s}')
    print(f'Total number of correct answers:{cnt_total}')


def single_problem(file_path,printLog):
    solve_program1.solve(file_path,printLog)
    solve_program2.solve(file_path,printLog)

    #　条件可視化
    graph.show_graph(file_path)
    
    

# メインプログラムとして実行された場合にmain()を呼び出す
if __name__ == "__main__":
    single_problem("json/shift_data200.json",True)
    # multiple_problem(False)