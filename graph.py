import json
import matplotlib.pyplot as plt
import numpy as np

def show_graph(file_path):
    # JSONファイルからデータを読み込む
    with open(file_path, "r") as f:
        shift_data = json.load(f)

    data = {
        "required_employees": shift_data["required_employees"],
        "shift_patterns": shift_data["shift_patterns"],
        "preferences": shift_data["preferences"],
        "unavailable_slots": shift_data["unavailable_slots"]
    }

    # 各データの可視化
    fig, axs = plt.subplots(3, 1, figsize=(10, 12))
    fig.tight_layout(pad=5.0)

    # 必要な従業員数
    axs[0].bar(range(len(data["required_employees"])), data["required_employees"], color="skyblue")
    axs[0].set_title("Required Employees")
    axs[0].set_xlabel("Time Slot")
    axs[0].set_ylabel("Required number of employees")

    # シフトパターン
    axs[1].imshow(data["shift_patterns"], cmap="Blues", aspect="auto")
    axs[1].set_title("Shift Patterns")
    axs[1].set_xlabel("Time Slot")
    axs[1].set_ylabel("Patterns ID")

    # 従業員の希望
    axs[2].imshow(data["preferences"], cmap="Greens", aspect="auto",alpha=0.5)
    axs[2].imshow(data["unavailable_slots"], cmap="Reds", aspect="auto",alpha=0.5)
    axs[2].set_title("Employee's desired and unavailable work hours")
    axs[2].set_xlabel("Time Slot")
    axs[2].set_ylabel("Employee ID")

    plt.show()
