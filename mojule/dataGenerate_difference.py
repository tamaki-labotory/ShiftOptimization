import os
import json
import glob
import numpy as np
import random

def ensure_directories_exist(directories):
    """
    必要なディレクトリが存在しない場合は作成する。
    """
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)


def get_file_sets(directory):
    """
    指定されたディレクトリから3種類のJSONファイルセットを取得する。
    """
    shift_pattern_files = sorted(glob.glob(os.path.join(directory, "shift_patterns_1.json")))
    pref_unavail_files = sorted(glob.glob(os.path.join(directory, "preferences_and_unavailable_slots_1.json")))
    required_employee_files = sorted(glob.glob(os.path.join(directory, "required_employees_1.json")))

    return list(zip(shift_pattern_files, pref_unavail_files, required_employee_files))


def load_json(file_path):
    """
    JSONファイルを読み込み、辞書を返す。
    """
    with open(file_path, "r") as f:
        return json.load(f)

##一つの勤務可能を勤務不可に変更
def create_difference_problem_1(i, shift_patterns, preferences, unavailable_slots, required_employees):

    # unavailable_slotsをコピーして変更
    modified_unavailable_slots = [row[:] for row in unavailable_slots]  # 元のデータを破壊しないようコピー
    modified_preferences = [row[:] for row in preferences]

    # 0の箇所をランダムに1つ選び、1に変更
    zero_positions = [
        (row_index, col_index)
        for row_index, row in enumerate(modified_unavailable_slots)
        for col_index, value in enumerate(row) if value == 0
    ]

    change_position = None  # 初期値（変更がない場合はNoneのまま）
    if zero_positions:  # 0の箇所が存在する場合のみ変更
        change_position = random.choice(zero_positions)
        row_index, col_index = change_position
        modified_unavailable_slots[row_index][col_index] = 1
        if preferences[row_index][col_index] == 1:
            modified_preferences[row_index][col_index] = 0


    """
    シフトデータをファイルに保存する。
    """
    # 必要なディレクトリを作成
    ensure_directories_exist(["json", "txt"])

    # JSON保存
    # JSON保存
    with open(f"json/shift_patterns_difference_{i}.json", "w") as f:
        json.dump({"shift_patterns": shift_patterns}, f, indent=4)

    with open(f"json/preferences_and_unavailable_slots_difference_{i}.json", "w") as f:
        json.dump(
            {"preferences": modified_preferences, "unavailable_slots": modified_unavailable_slots},
            f,
            indent=4
        )

    with open(f"json/required_employees_difference_{i}.json", "w") as f:
        json.dump({"required_employees": required_employees}, f, indent=4)

    # TXT保存
    with open(f"txt/shift_patterns_difference_{i}.txt", "w") as f:
        f.write(f"shift_patterns:\n{shift_patterns}\n")

    with open(f"txt/preferences_and_unavailable_slots_difference_{i}.txt", "w") as f:
        f.write(f"preferences:\n{modified_preferences}\n")
        f.write(f"unavailable_slots:\n{modified_unavailable_slots}\n")
        if change_position:
            f.write(f"\nChanged position: {change_position}\n")

    with open(f"txt/required_employees_difference_{i}.txt", "w") as f:
        f.write(f"required_employees:\n{required_employees}\n")

    # 変更箇所を出力
    if change_position:
        print(f"Problem {i}: Changed position in unavailable_slots -> Row: {change_position[0]}, Column: {change_position[1]}")
    else:
        print(f"Problem {i}: No changes made to unavailable_slots (no 0 found).")





##勤務不可がランダムにnum_changes箇所追加
def create_difference_problem_2(i, shift_patterns, preferences, unavailable_slots, required_employees, num_changes):

    # unavailable_slotsをコピーして変更
    modified_unavailable_slots = [row[:] for row in unavailable_slots]  # 元のデータを破壊しないようコピー
    modified_preferences = [row[:] for row in preferences]

    # 0の箇所をリストアップ
    zero_positions = [
        (row_index, col_index)
        for row_index, row in enumerate(modified_unavailable_slots)
        for col_index, value in enumerate(row) if value == 0
    ]

    # 変更箇所をランダムに選択
    changed_positions = []  # 実際に変更された位置を記録
    for _ in range(min(num_changes, len(zero_positions))):
        change_position = random.choice(zero_positions)
        zero_positions.remove(change_position)  # 選ばれた箇所をリストから除外
        row_index, col_index = change_position
        modified_unavailable_slots[row_index][col_index] = 1
        if preferences[row_index][col_index] == 1:
            modified_preferences[row_index][col_index] = 0
        changed_positions.append(change_position)

    # 必要なディレクトリを作成
    ensure_directories_exist(["json", "txt"])

    # JSON保存
    with open(f"json/shift_patterns_difference_{i}.json", "w") as f:
        json.dump({"shift_patterns": shift_patterns}, f, indent=4)

    with open(f"json/preferences_and_unavailable_slots_difference_{i}.json", "w") as f:
        json.dump(
            {"preferences": modified_preferences, "unavailable_slots": modified_unavailable_slots},
            f,
            indent=4
        )

    with open(f"json/required_employees_difference_{i}.json", "w") as f:
        json.dump({"required_employees": required_employees}, f, indent=4)

    # TXT保存
    with open(f"txt/shift_patterns_difference_{i}.txt", "w") as f:
        f.write(f"shift_patterns:\n{shift_patterns}\n")

    with open(f"txt/preferences_and_unavailable_slots_difference_{i}.txt", "w") as f:
        f.write(f"preferences:\n{modified_preferences}\n")
        f.write(f"unavailable_slots:\n{modified_unavailable_slots}\n")
        if changed_positions:
            f.write(f"\nChanged positions: {changed_positions}\n")

    with open(f"txt/required_employees_difference_{i}.txt", "w") as f:
        f.write(f"required_employees:\n{required_employees}\n")

    # 変更箇所を出力
    if changed_positions:
        print(f"Problem {i}: Changed positions in unavailable_slots -> {changed_positions}")
    else:
        print(f"Problem {i}: No changes made to unavailable_slots (no 0 found).")

##必要人数がnum_changes個ランダムに増加
def create_difference_problem_3(i, shift_patterns, preferences, unavailable_slots, required_employees, num_changes):

    # 元のデータを破壊しないようコピー
    modified_required_employees = required_employees.copy()  


    # 変更箇所をランダムに選択
    changed_positions = []  # 実際に変更された位置を記録
    for _ in range(num_changes):
        #0から時間帯数でとりたい
        change_position = random.randint(0,len(modified_required_employees))
        modified_required_employees[change_position-1] += 1
        changed_positions.append(change_position)

    # 必要なディレクトリを作成
    ensure_directories_exist(["json", "txt"])

    # JSON保存
    with open(f"json/shift_patterns_difference_{i}.json", "w") as f:
        json.dump({"shift_patterns": shift_patterns}, f, indent=4)

    with open(f"json/preferences_and_unavailable_slots_difference_{i}.json", "w") as f:
        json.dump(
            {"preferences": preferences, "unavailable_slots": unavailable_slots},
            f,
            indent=4
        )

    with open(f"json/required_employees_difference_{i}.json", "w") as f:
        json.dump({"required_employees": modified_required_employees}, f, indent=4)

    # TXT保存
    with open(f"txt/shift_patterns_difference_{i}.txt", "w") as f:
        f.write(f"shift_patterns:\n{shift_patterns}\n")

    with open(f"txt/preferences_and_unavailable_slots_difference_{i}.txt", "w") as f:
        f.write(f"preferences:\n{preferences}\n")
        f.write(f"unavailable_slots:\n{unavailable_slots}\n")
        if changed_positions:
            f.write(f"\nChanged positions: {changed_positions}\n")

    with open(f"txt/required_employees_difference_{i}.txt", "w") as f:
        f.write(f"required_employees:\n{modified_required_employees}\n")

    # 変更箇所を出力
    if changed_positions:
        print(f"Problem {i}: Changed positions in required_employees -> {changed_positions}")
    else:
        print(f"Problem {i}: No changes made to required_employees  (no 0 found).")


def process_files(directory, num_iterations):
    """
    ファイルを処理して、問題データを生成する。
    :param directory: JSONファイルのディレクトリ
    :param num_iterations: 各データセットに対してcreate_difference_problem_1を回す回数
    """
    file_sets = get_file_sets(directory)

    for file_index, (shift_pattern_file, pref_unavail_file, required_employee_file) in enumerate(file_sets):
        # 各ファイルからデータを読み込む
        shift_patterns = load_json(shift_pattern_file)["shift_patterns"]
        pref_unavail_data = load_json(pref_unavail_file)
        preferences = pref_unavail_data["preferences"]
        unavailable_slots = pref_unavail_data["unavailable_slots"]
        required_employees = load_json(required_employee_file)["required_employees"]

        # 指定された回数だけ問題データを生成
        for iteration in range(num_iterations):
            problem_index =  iteration
            create_difference_problem_3(problem_index, shift_patterns, preferences, unavailable_slots, required_employees,1)


# メイン処理
if __name__ == "__main__":
    # 任意のディレクトリと回数を指定可能
    directory = "/Users/hymac/mypy/ShiftOptimization-progress1/json/"
    num_iterations = 20  # 各データセットに対する繰り返し回数

    process_files(directory, num_iterations)


