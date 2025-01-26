import sys
import os
# プロジェクトのルートディレクトリをsys.pathに追加
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import glob
import numpy as np
import openpyxl
from matsu import shift_scheduler1
from matsu import shift_scheduler2
from matsu import shift_scheduler3
from matsu import shift_scheduler4
from matsu import shift_scheduler5
from matsu import shift_scheduler6
from matsu import shift_scheduler7
from matsu import shift_scheduler8
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
    # 各スケジューラーの結果を記録する変数
    cnt1_f = cnt1_s = cnt1_total = 0
    cnt2_f = cnt2_s = cnt2_total = 0
    cnt3_s = cnt3_total = 0
    cnt4_s = cnt4_total = 0
    cnt5_s = cnt5_total = 0
    over_labors = [[], [], [], [], []]
    negative_labors = [[], [], [], [], []]
    fulfill_preferences = [[], [], [], [], []]
    time_1 = [[], [], [], [], []]
    time_2 = [[], [], [], [], []]

    # ディレクトリ指定
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
        ShiftScheduler4 = shift_scheduler4.ShiftScheduler4(file_paths, printLog)
        ShiftScheduler5 = shift_scheduler5.ShiftScheduler5(file_paths, printLog)
        ShiftScheduler6 = shift_scheduler6.ShiftScheduler6(file_paths, printLog)
        ShiftScheduler7 = shift_scheduler7.ShiftScheduler7(file_paths, printLog)
        ShiftScheduler8 = shift_scheduler8.ShiftScheduler8(file_paths, printLog)

        # 各スケジューラーを解く
        ShiftScheduler4.solve()
        ShiftScheduler5.solve()
        ShiftScheduler6.solve()
        ShiftScheduler7.solve()
        ShiftScheduler8.solve()

        # ログ表示と結果収集
        append_flag = True
        if printLog:
            print(f"\n~~~~ Results of Problem {os.path.basename(shift_pattern_file)} ~~~~")

        # スケジューラー4の結果
        ret.append(ShiftScheduler4.ret)
        if ret[-1][0] == 1:
            cnt1_f += 1
        if ret[-1][1] == 1:
            cnt1_s += 1
        if ret[-1][0] == 1 and ret[-1][1] == 1:
            cnt1_total += 1
        else:
            append_flag = False
        if printLog:
            ShiftScheduler4.print_results()
            print("~~~~~~~~~~~~~~~~~~~~~~")

        # スケジューラー5の結果
        ret.append(ShiftScheduler5.ret)
        if ret[-1][0] == 1:
            cnt2_f += 1
        if ret[-1][1] == 1:
            cnt2_s += 1
        if ret[-1][0] == 1 and ret[-1][1] == 1:
            cnt2_total += 1
        else:
            append_flag = False
        if printLog:
            ShiftScheduler5.print_results()
            print("~~~~~~~~~~~~~~~~~~~~~~")

        # スケジューラー6の結果
        ret.append(ShiftScheduler6.ret)
        if ret[-1][1] == 1:
            cnt3_s += 1
            cnt3_total += 1
        else:
            append_flag = False
        if printLog:
            ShiftScheduler6.print_results()
            print("~~~~~~~~~~~~~~~~~~~~~~")

        # スケジューラー7の結果
        ret.append(ShiftScheduler7.ret)
        if ret[-1][1] == 1:
            cnt4_s += 1
            cnt4_total += 1
        else:
            append_flag = False
        if printLog:
            ShiftScheduler7.print_results()
            print("~~~~~~~~~~~~~~~~~~~~~~")

        # スケジューラー8の結果
        ret.append(ShiftScheduler8.ret)
        if ret[-1][1] == 1:
            cnt5_s += 1
            cnt5_total += 1
        else:
            append_flag = False
        if printLog:
            ShiftScheduler8.print_results()
            print("~~~~~~~~~~~~~~~~~~~~~~")

        # 成功した場合のみ結果を記録
        if append_flag:
            for i in range(5):
                over_labors[i].append(ret[i][2])
                fulfill_preferences[i].append(ret[i][3])
                negative_labors[i].append(ret[i][6])
                time_1[i].append(ret[i][7])
                time_2[i].append(ret[i][8])

    # 平均値を計算する
    def calculate_average(data_list):
        return np.mean(data_list) if data_list else 0

    # 各リストの平均値を計算
    over_labors_avg = [calculate_average(over_labors[i]) for i in range(5)]
    negative_labors_avg = [calculate_average(negative_labors[i]) for i in range(5)]
    fulfill_preferences_avg = [calculate_average(fulfill_preferences[i]) for i in range(5)]
    time_1_avg = [calculate_average(time_1[i]) for i in range(5)]
    time_2_avg = [calculate_average(time_2[i]) for i in range(5)]

    # 実行可能解数の表示
    print("\n~~~~ Total Correct Answers ~~~~")
    print(f"Total correct answers (4th solver): {cnt1_total}")
    print(f"Total correct answers (5th solver): {cnt2_total}")
    print(f"Total correct answers (6th solver): {cnt3_total}")
    print(f"Total correct answers (7th solver): {cnt4_total}")
    print(f"Total correct answers (8th solver): {cnt5_total}")
    # ログ表示
    print(f"\n~~~~ Average Results ~~~~")
    for i, solver_name in enumerate(["4th", "5th", "6th", "7th", "8th"]):
        print(f"\nResults for {solver_name} solver:")
        print(f"Overstaffing Hours Average: {over_labors_avg[i]}")
        print(f"Negative Labors Average: {negative_labors_avg[i]}")
        print(f"Fulfill Preferences Average: {fulfill_preferences_avg[i]}")
        print(f"Time for 1st Stage Average: {time_1_avg[i]}")
        print(f"Time for 2nd Stage Average: {time_2_avg[i]}")
    # エクセルファイルへの書き込み
    excel_path = "/Users/hymac/Desktop/学校/0128.xlsx"
    sheet_number = 1  # 手動で指定するシート番号
    problem_number = 1  # 手動で指定する問題番号

    # エクセルファイルを読み込み
    wb = openpyxl.load_workbook(excel_path)
    sheet_name = f"Sheet{sheet_number}"
    if sheet_name not in wb.sheetnames:
        raise ValueError(f"指定されたシート番号 {sheet_number} に対応するシートが見つかりません。")

    sheet = wb[sheet_name]

    # データ書き込み
    base_row = 2  # 問題番号に基づく行の基準
    sheet[f"B{base_row}"] = cnt1_total  # 実行可能解数
    sheet[f"B{base_row + 1}"] = negative_labors_avg[0]
    sheet[f"B{base_row + 2}"] = over_labors_avg[0]
    sheet[f"B{base_row + 3}"] = fulfill_preferences_avg[0]
    sheet[f"B{base_row + 4}"] = time_1_avg[0]
    sheet[f"B{base_row + 5}"] = time_2_avg[0]

        # エクセルファイルを読み込み
    wb = openpyxl.load_workbook(excel_path)
    sheet_name = f"Sheet{sheet_number}"
    if sheet_name not in wb.sheetnames:
        raise ValueError(f"指定されたシート番号 {sheet_number} に対応するシートが見つかりません。")

    sheet = wb[sheet_name]

    # 列のアルファベット計算（問題番号に応じて列を遷移）
    column_letter = chr(ord('B') + (problem_number - 1))

    # データ書き込み
    base_rows = [2, 10, 18, 26, 34]  # 各スケジューラーのbase_row
    totals = [cnt1_total, cnt2_total, cnt3_total, cnt4_total, cnt5_total]
    averages = [negative_labors_avg, over_labors_avg, fulfill_preferences_avg, time_1_avg, time_2_avg]

    for i, base_row in enumerate(base_rows):
        # 実行可能解数
        sheet[f"{column_letter}{base_row}"] = totals[i]
        # 各平均値を記入
        for j, avg in enumerate(averages):
            sheet[f"{column_letter}{base_row + j + 1}"] = avg[i]
    # エクセルファイルを保存
    wb.save(excel_path)
    print(f"結果がエクセルファイルに保存されました: {excel_path}")
    
    # グラフ表示
    sdv = graph.ShiftDataVisualizer()
    sdv.show_scatter(over_labors, fulfill_preferences)



def single_problem(file_paths, printLog):
    """
    file_paths: 辞書形式でファイルパスを指定
    """
    ShiftScheduler4 = shift_scheduler4.ShiftScheduler4(file_paths, printLog)
    ShiftScheduler4.solve()
    ShiftScheduler4.print_results()
    print("~~~~~~~~~~~~~~~~~~~~~~")

    ShiftScheduler5 = shift_scheduler6.ShiftScheduler6(file_paths, printLog)
    ShiftScheduler5.solve()
    ShiftScheduler5.print_results()
    print("~~~~~~~~~~~~~~~~~~~~~~")

    ShiftScheduler6 = shift_scheduler7.ShiftScheduler7(file_paths, printLog)
    ShiftScheduler6.solve()
    ShiftScheduler6.print_results()

    # グラフ表示
    sdv = graph.ShiftDataVisualizer(file_paths=file_paths)
    sdv.show_graph()
    #sdv.show_shift()
    #sdv.show_prefere()
    #sdv.show_number_of_labor()
    sdv.show_assingn_state(ShiftScheduler6.ret[5])


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
