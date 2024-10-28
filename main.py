import graph
import solve_program1

def main():
    # JSONファイルのパス
    file_path = "shift_data.json"

    #　条件可視化
    graph.show_graph(file_path)
    
    # 最適化プログラム実行
    solve_program1(file_path).solve
    

# メインプログラムとして実行された場合にmain()を呼び出す
if __name__ == "__main__":
    main()