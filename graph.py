"""
時間帯ごとのシフトパターンや必要人数を描画するプログラム
"""

import json
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import ListedColormap, BoundaryNorm

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

    plt.style.use("ggplot")

    fig, axs = plt.subplots(3, 1, figsize=(10, 14))
    fig.tight_layout(pad=6.0)

    # 1. 必要な従業員数のグラフ
    axs[0].bar(range(len(data["required_employees"])), data["required_employees"], color="skyblue", edgecolor="black")
    axs[0].set_title("Required Employees", fontsize=14, fontweight="bold")
    axs[0].set_xlabel("Time Slot", fontsize=12)
    axs[0].set_ylabel("Required Number of Employees", fontsize=12)
    axs[0].grid(axis="y", linestyle="--", alpha=0.7)
    axs[0].set_xticks(np.arange(len(np.array(data["required_employees"]))), minor=False)  # Major ticks at integers
    axs[0].set_xticks(np.arange(-0.5, len(np.array(data["required_employees"]))), minor=True)  # Minor ticks for grid lines
    axs[0].set_xticklabels(np.arange(1, len(np.array(data["required_employees"])) + 1))  # 整数ラベルのみ
    axs[0].set_xlim(-0.5,len(np.array(data["required_employees"]))-0.5)

    # 2. シフトパターンのヒートマップ
    shift_img = axs[1].imshow(data["shift_patterns"], cmap="Blues", aspect="auto")
    axs[1].set_title("Shift Patterns", fontsize=14, fontweight="bold")
    axs[1].set_xlabel("Time Slot", fontsize=12)
    axs[1].set_ylabel("Pattern ID", fontsize=12)

    axs[1].set_xticks(np.arange(np.array(data["shift_patterns"]).shape[1]), minor=False)  # Major ticks at integers
    axs[1].set_yticks(np.arange(np.array(data["shift_patterns"]).shape[0]), minor=False)
    axs[1].set_xticks(np.arange(-0.5, np.array(data["shift_patterns"]).shape[1]), minor=True)  # Minor ticks for grid lines
    axs[1].set_yticks(np.arange(-0.5, np.array(data["shift_patterns"]).shape[0]), minor=True)
    axs[1].set_xticklabels(np.arange(1, np.array(data["shift_patterns"]).shape[1] + 1))  # 整数ラベルのみ
    axs[1].set_yticklabels(np.arange(1, np.array(data["shift_patterns"]).shape[0] + 1))
    axs[1].grid(which="both", color="gray", linestyle="--", linewidth=0.5)
    axs[1].grid(which="major", color="none")

    # 3. 従業員の希望と利用不可スロットのオーバーレイ
    pref_img = axs[2].imshow(data["preferences"], cmap=ListedColormap(["white", "Green"]), aspect="auto", alpha=0.5)
    unavail_img = axs[2].imshow(data["unavailable_slots"], cmap=ListedColormap(["white", "Red"]), aspect="auto", alpha=0.5)
    axs[2].set_title("Employee Preferences and Unavailable Slots", fontsize=14, fontweight="bold")
    axs[2].set_xlabel("Time Slot", fontsize=12)
    axs[2].set_ylabel("Employee ID", fontsize=12)
   
    axs[2].set_xticks(np.arange(np.array(data["unavailable_slots"]).shape[1]), minor=False)  # Major ticks at integers
    axs[2].set_yticks(np.arange(np.array(data["unavailable_slots"]).shape[0]), minor=False)
    axs[2].set_xticks(np.arange(-0.5, np.array(data["unavailable_slots"]).shape[1]), minor=True)  # Minor ticks for grid lines
    axs[2].set_yticks(np.arange(-0.5, np.array(data["unavailable_slots"]).shape[0]), minor=True)
    axs[2].set_xticklabels(np.arange(1, np.array(data["unavailable_slots"]).shape[1] + 1))  # 整数ラベルのみ
    axs[2].set_yticklabels(np.arange(1, np.array(data["unavailable_slots"]).shape[0] + 1))
    axs[2].grid(which="both", color="gray", linestyle="--", linewidth=0.5)
    axs[2].grid(which="major", color="none")


    # レジェンドの作成
    from matplotlib.lines import Line2D
    legend_elements = [
        Line2D([0], [0], color="green", lw=4, label="Preferences"),
        Line2D([0], [0], color="red", lw=4, label="Unavailable Slots")
    ]
    axs[2].legend(handles=legend_elements, loc="upper right", fontsize=10)

    plt.show()
