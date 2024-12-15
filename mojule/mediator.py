import sys
import os
# プロジェクトのルートディレクトリをsys.pathに追加
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import glob
import numpy as np
from matsu import shift_scheduler1
from matsu import shift_scheduler2
from matsu import shift_scheduler3
import graph

def get_file_sets(directory):
    """
    指定されたディレクトリから3種類のJSONファイルセットを取得する。
    """
    shift_pattern_files = sorted(glob.glob(os.path.join(directory, "shift_patterns_*.json")))
    pref_unavail_files = sorted(glob.glob(os.path.join(directory, "preferences_and_unavailable_slots_*.json")))
    required_employee_files = sorted(glob.glob(os.path.join(directory, "required_employees_*.json")))

    return list(zip(shift_pattern_files, pref_unavail_files, required_employee_files))

def multiple_problem(printLog):
    cnt1_f = cnt1_s = cnt1_total = 0
    cnt2_s = cnt2_total = 0
    cnt3_f = cnt3_s = cnt3_total = 0
    over_labors = [[], [], []]
    fulfill_preferences = [[], [], []]

    # 帆前環境用：ディレクトリ指定
    directory = "/Users/hymac/mypy/ShiftOptimization-progress1/json/"
    file_sets = get_file_sets(directory)

    for shift_pattern_file, pref_unavail_file, required_employee_file in file_sets:
        file_paths = {
            "shift_patterns": shift_pattern_file,
            "preferences_and_unavailable_slots": pref_unavail_file,
            "required_employees": required_employee_file,
        }

        ret = []

        # 各シフトスケジューラーのインスタンス作成
        ShiftScheduler1 = shift_scheduler1.ShiftScheduler1(file_paths, printLog)
        ShiftScheduler2 = shift_scheduler2.ShiftScheduler2(file_paths, printLog)
        ShiftScheduler3 = shift_scheduler3.ShiftScheduler3(file_paths, printLog)

        # 各スケジューラーを解く
        ShiftScheduler1.solve()
        ShiftScheduler2.solve()
        ShiftScheduler3.solve()

        # ログ表示と結果収集
        append_flag = True
        if printLog:
            print(f"\n~~~~ Results of Problem {os.path.basename(shift_pattern_file)} ~~~~")

        # 1つ目のプログラム結果
        ret.append(ShiftScheduler1.ret)
        if ret[-1][0] == 1:
            cnt1_f += 1
        if ret[-1][1] == 1:
            cnt1_s += 1
        if ret[-1][0] == 1 and ret[-1][1] == 1:
            cnt1_total += 1
        else:
            append_flag = False
        if printLog:
            ShiftScheduler1.print_results()
            print("~~~~~~~~~~~~~~~~~~~~~~")

        # 2つ目のプログラム結果
        ret.append(ShiftScheduler2.ret)
        if ret[-1][1] == 1:
            cnt2_s += 1
            cnt2_total += 1
        else:
            append_flag = False
        if printLog:
            ShiftScheduler2.print_results()
            print("~~~~~~~~~~~~~~~~~~~~~~")

        # 3つ目のプログラム結果
        ret.append(ShiftScheduler3.ret)
        if ret[-1][0] == 1:
            cnt3_f += 1
        if ret[-1][1] == 1:
            cnt3_s += 1
        if ret[-1][0] == 1 and ret[-1][1] == 1:
            cnt3_total += 1
        else:
            append_flag = False
        if printLog:
            ShiftScheduler3.print_results()

        # 成功した場合のみ結果を記録
        if append_flag:
            for i in range(3):
                over_labors[i].append(ret[i][2])
                fulfill_preferences[i].append(ret[i][3])

    print(f"plot data: {np.array(over_labors).shape[1]}")

    # ログ表示
    print(f"\nNumber of correct answers in the first stage: {cnt1_f}")
    print(f"Number of correct answers in the second stage: {cnt1_s}")
    print(f"Total number of correct answers: {cnt1_total}")
    print(f"Number of correct answers in the second stage (2nd solver): {cnt2_s}")
    print(f"Total number of correct answers (2nd solver): {cnt2_total}")
    print(f"Number of correct answers in the first stage (3rd solver): {cnt3_f}")
    print(f"Number of correct answers in the second stage (3rd solver): {cnt3_s}")
    print(f"Total number of correct answers (3rd solver): {cnt3_total}")

    # グラフ表示
    sdv = graph.ShiftDataVisualizer()
    sdv.show_scatter(over_labors, fulfill_preferences)


def single_problem(file_paths, printLog):
    """
    file_paths: 辞書形式でファイルパスを指定
    """
    ShiftScheduler1 = shift_scheduler1.ShiftScheduler1(file_paths, printLog)
    ShiftScheduler1.solve()
    ShiftScheduler1.print_results()
    print("~~~~~~~~~~~~~~~~~~~~~~")

    ShiftScheduler2 = shift_scheduler2.ShiftScheduler2(file_paths, printLog)
    ShiftScheduler2.solve()
    ShiftScheduler2.print_results()
    print("~~~~~~~~~~~~~~~~~~~~~~")

    ShiftScheduler3 = shift_scheduler3.ShiftScheduler3(file_paths, printLog)
    ShiftScheduler3.solve()
    ShiftScheduler3.print_results()

    # グラフ表示
    sdv = graph.ShiftDataVisualizer(file_paths=file_paths)
    sdv.show_graph()
    #sdv.show_assingn_state(ShiftScheduler3.ret[4])


def mediator(s_or_m, input_path, printLog):
    """
    s_or_m: 's' -> single problem, 'm' -> multiple problem
    input_path: ファイルまたはディレクトリのパス
    """
    if s_or_m == 's':
    # シングル問題の場合、ファイルセットを構築
        file_paths = {
            "shift_patterns": input_path["shift_patterns"],
            "preferences_and_unavailable_slots": input_path["preferences_and_unavailable_slots"],
            "required_employees": input_path["required_employees"],
        }
        single_problem(file_paths, printLog)

    elif s_or_m == 'm':
        multiple_problem(printLog)
    else:
        print("Invalid input. Please input 's' or 'm' as the first argument.")
