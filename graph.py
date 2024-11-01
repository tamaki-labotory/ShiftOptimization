"""
時間帯ごとのシフトパターンや必要人数を描画するプログラム
"""

import json
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import ListedColormap, BoundaryNorm



class ShiftDataVisualizer:
    def __init__(self,file_path=None,data=None):
        if file_path!=None:
            self.data=self._load_data(file_path)
        if data!=None:
            self.data=data


    def _load_data(self,file_path):
        """JSONファイルからデータを読み込むメソッド"""
        with open(file_path, "r") as f:
            shift_data = json.load(f)
        
        return {
            "required_employees": shift_data["required_employees"],
            "shift_patterns": shift_data["shift_patterns"],
            "preferences": shift_data["preferences"],
            "unavailable_slots": shift_data["unavailable_slots"]
        }
      
    def show_graph(self):
        plt.style.use("ggplot")

        fig, axs = plt.subplots(3, 1, figsize=(10, 14))
        fig.tight_layout(pad=6.0)

        # 1. 必要な従業員数のグラフ
        axs[0].bar(range(len(self.data["required_employees"])), self.data["required_employees"], color="skyblue", edgecolor="black")
        axs[0].set_title("Required Employees", fontsize=14, fontweight="bold")
        axs[0].set_xlabel("Time Slot", fontsize=12)
        axs[0].set_ylabel("Required Number of Employees", fontsize=12)
        axs[0].grid(axis="y", linestyle="--", alpha=0.7)
        axs[0].set_xticks(np.arange(len(np.array(self.data["required_employees"]))), minor=False)  # Major ticks at integers
        axs[0].set_xticks(np.arange(-0.5, len(np.array(self.data["required_employees"]))), minor=True)  # Minor ticks for grid lines
        axs[0].set_xticklabels(np.arange(1, len(np.array(self.data["required_employees"])) + 1))  # 整数ラベルのみ
        axs[0].set_xlim(-0.5,len(np.array(self.data["required_employees"]))-0.5)

        # 2. シフトパターンのヒートマップ
        shift_img = axs[1].imshow(self.data["shift_patterns"], cmap="Blues", aspect="auto")
        axs[1].set_title("Shift Patterns", fontsize=14, fontweight="bold")
        axs[1].set_xlabel("Time Slot", fontsize=12)
        axs[1].set_ylabel("Pattern ID", fontsize=12)

        axs[1].set_xticks(np.arange(np.array(self.data["shift_patterns"]).shape[1]), minor=False)  # Major ticks at integers
        axs[1].set_yticks(np.arange(np.array(self.data["shift_patterns"]).shape[0]), minor=False)
        axs[1].set_xticks(np.arange(-0.5, np.array(self.data["shift_patterns"]).shape[1]), minor=True)  # Minor ticks for grid lines
        axs[1].set_yticks(np.arange(-0.5, np.array(self.data["shift_patterns"]).shape[0]), minor=True)
        axs[1].set_xticklabels(np.arange(1, np.array(self.data["shift_patterns"]).shape[1] + 1))  # 整数ラベルのみ
        axs[1].set_yticklabels(np.arange(1, np.array(self.data["shift_patterns"]).shape[0] + 1))
        axs[1].grid(which="both", color="gray", linestyle="--", linewidth=0.5)
        axs[1].grid(which="major", color="none")

        # 3. 従業員の希望と利用不可スロットのオーバーレイ
        pref_img = axs[2].imshow(self.data["preferences"], cmap=ListedColormap(["white", "Green"]), aspect="auto", alpha=0.5)
        unavail_img = axs[2].imshow(self.data["unavailable_slots"], cmap=ListedColormap(["white", "Red"]), aspect="auto", alpha=0.5)
        axs[2].set_title("Employee Preferences and Unavailable Slots", fontsize=14, fontweight="bold")
        axs[2].set_xlabel("Time Slot", fontsize=12)
        axs[2].set_ylabel("Employee ID", fontsize=12)
    
        axs[2].set_xticks(np.arange(np.array(self.data["unavailable_slots"]).shape[1]), minor=False)  # Major ticks at integers
        axs[2].set_yticks(np.arange(np.array(self.data["unavailable_slots"]).shape[0]), minor=False)
        axs[2].set_xticks(np.arange(-0.5, np.array(self.data["unavailable_slots"]).shape[1]), minor=True)  # Minor ticks for grid lines
        axs[2].set_yticks(np.arange(-0.5, np.array(self.data["unavailable_slots"]).shape[0]), minor=True)
        axs[2].set_xticklabels(np.arange(1, np.array(self.data["unavailable_slots"]).shape[1] + 1))  # 整数ラベルのみ
        axs[2].set_yticklabels(np.arange(1, np.array(self.data["unavailable_slots"]).shape[0] + 1))
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


    def show_scatter(self,over_labors,fulfill_preferences):
        # 散布図作成
        plt.figure(figsize=(10, 6))

        # 各行のデータをプロット
        for idx in range(len(over_labors)):
            plt.scatter(over_labors[idx], fulfill_preferences[idx], label=f'Row {idx+1}', alpha=0.7)

        # グラフの設定
        plt.title('Scatter Plot of Over Labors vs Fulfill Preferences (Each Row Grouped by Color)')
        plt.xlabel('Over Labors Values')
        plt.ylabel('Fulfill Preferences Values')
        plt.legend()
        plt.grid(True)
        plt.show()
    

    def show_scatter_using_heat_map(self,data,points=[],xlabel="Objective1",ylabel="Objective2",title="Plot of each data value in the objective functions 1 and 2",colorbar_label=""):
        # 値の大きさに応じたカラー設定
        data_sum = np.array(data[0]) + np.array(data[1])

        plt.figure(figsize=(10, 6))
        
        # 各行のデータをプロット（合計値をカラーマップで指定）
        plt.scatter(data[0], data[1], c=data_sum, cmap='plasma', alpha=0.7)

        for point in points:
            plt.scatter(point[0],point[1],marker='x')

        # カラーバーを追加して色の基準を表示
        plt.colorbar(label=colorbar_label)


        # グラフの設定
        plt.title(title)
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.grid(True)
        plt.show()
