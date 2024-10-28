import graph
import solve_program1

def multiple_problem(printLog):
    cnt_f=0
    cnt_s=0
    cnt_total=0
    for i in range(200):
        # JSONファイルのパス
        file_path = f"json/shift_data{i+1}.json"

        # 最適化プログラム実行
        if printLog:
            print(f"\n~~~~Results of Problem{i+1}~~~~")
        result1,result2=solve_program1.solve(file_path,printLog)
        if result1==1:
            cnt_f+=1
        if result2==1:
            cnt_s+=1
        if result1==1 and result2==1:
            cnt_total+=1
    print(f'\nNumber of correct answers in the first stage:{cnt_f}')
    print(f'Number of correct answers in the second stage:{cnt_s}')
    print(f'Total number of correct answers:{cnt_total}')


def single_problem(file_path):
    solve_program1.solve(file_path)

    #　条件可視化
    graph.show_graph(file_path)
    
    

# メインプログラムとして実行された場合にmain()を呼び出す
if __name__ == "__main__":
    # single_problem("json/shift_data200.json")
    multiple_problem(False)