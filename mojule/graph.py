"""
時間帯ごとのシフトパターンや必要人数を描画するプログラム
"""

import json
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import ListedColormap, BoundaryNorm



class ShiftDataVisualizer:
    def __init__(self, file_paths=None, data=None):
        if file_paths is not None:
            self.data = self._load_data(file_paths)
            print("Loaded data:", self.data)  # デバッグ用にデータを出力
        elif data is not None:
            self.data = data
            print("11111111111")  
        else:
            self.data = {}  # デフォルト値として空の辞書を設定
            print("222222222222")  

    def _load_data(self, file_paths):
        """
        3つのJSONファイルからデータを読み込むメソッド。

        file_paths: 辞書形式で各ファイルパスを指定
            {
                "shift_patterns": "path/to/shift_patterns.json",
                "preferences_and_unavailable_slots": "path/to/preferences_and_unavailable_slots.json",
                "required_employees": "path/to/required_employees.json"
            }
        """
        try:
            # シフトパターン
            with open(file_paths["shift_patterns"], "r") as f:
                shift_patterns = json.load(f)["shift_patterns"]

            # 希望と不可スロット
            with open(file_paths["preferences_and_unavailable_slots"], "r") as f:
                pref_unavail_data = json.load(f)
                preferences = pref_unavail_data["preferences"]
                unavailable_slots = pref_unavail_data["unavailable_slots"]

            # 必要人数
            with open(file_paths["required_employees"], "r") as f:
                required_employees = json.load(f)["required_employees"]

            # データ統合
            return {
                "required_employees": required_employees,
                "shift_patterns": shift_patterns,
                "preferences": preferences,
                "unavailable_slots": unavailable_slots
            }

        except KeyError as e:
            print(f"Missing key in the data files: {e}")
            raise
        except FileNotFoundError as e:
            print(f"File not found: {e}")
            raise
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
            raise

      
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

    def show_assingn_state(self, assigned_shifts):
        plt.style.use("ggplot")  # グラフのスタイルを設定
        if not self.data:
            raise ValueError("No data available. Please provide a valid file_path or data.")
        if "required_employees" not in self.data or "shift_patterns" not in self.data:
            raise ValueError("The data does not contain required keys: 'required_employees' or 'shift_patterns'.")

        fig, ax = plt.subplots(figsize=(12, 8))  # グラフのサイズを設定

        time_slots = len(self.data["required_employees"])
        num_shifts = len(self.data["shift_patterns"])

        # 割り当てられたシフトをマトリックス形式に変換
        assigned_matrix = np.zeros((time_slots, num_shifts))
        for i, shift_pattern in enumerate(self.data["shift_patterns"]):
            if assigned_shifts[i] > 0:
                assigned_matrix[:, i] = np.array(shift_pattern) * assigned_shifts[i]

        pastel_colors = [
            "#FFB6C1",  # Light Pink
            "#FFD700",  # Gold
            "#87CEEB",  # Sky Blue
            "#98FB98",  # Pale Green
            "#FF69B4",  # Hot Pink
            "#FFA07A",  # Light Salmon
            "#DDA0DD",  # Plum
            "#E6E6FA",  # Lavender
            "#F5DEB3",  # Wheat
            "#FFC0CB",  # Pink
        ]

        # 各シフトをスタックして描画
        bottom = np.zeros(time_slots)
        for i in range(num_shifts):
            if assigned_shifts[i] > 0:
                ax.bar(
                    range(time_slots),
                    assigned_matrix[:, i],
                    bottom=bottom,
                    color=pastel_colors[i % len(pastel_colors)],  # パステル系の色を適用
                    edgecolor="black",
                    linewidth=0.8,
                    label=f"Shift {i + 1} (Assigned: {assigned_shifts[i]})",
                )
                bottom += assigned_matrix[:, i]

        # 必要人数を超えた部分を計算
        total_assigned = np.sum(assigned_matrix, axis=1)
        over_assignment = total_assigned - self.data["required_employees"]
        over_assignment[over_assignment < 0] = 0  # 超過していない部分はゼロにする

        # 必要人数ラインの描画
        ax.plot(
            range(time_slots),
            self.data["required_employees"],
            "r-",
            linewidth=2,
            marker="o",
            markersize=6,
            label="Required Employees",
        )

        # 必要人数を超えた部分にハッチングを追加
        ax.bar(
            range(time_slots),
            over_assignment,
            bottom=self.data["required_employees"],
            color="none",  # 塗りつぶしなし
            edgecolor="black",
            hatch="///",  # ハッチングパターン
            linewidth=1.0,
            label="Over Assignment (Hatched)",
        )

        # y軸の上方向に余裕を持たせる
        max_y = max(np.max(total_assigned), np.max(self.data["required_employees"]))
        ax.set_ylim(0, max_y * 1.2)  # 最大値の20%余裕を追加

        # グラフの詳細設定
        ax.set_title("Assigned Shifts and Over Assignment", fontsize=16, fontweight="bold")
        ax.set_xlabel("Time Slot", fontsize=12)
        ax.set_ylabel("Number of Employees", fontsize=12)
        ax.set_xticks(range(time_slots))
        ax.set_xticklabels(range(1, time_slots + 1))
        ax.legend(fontsize=10)
        ax.grid(axis="y", linestyle="--", alpha=0.7)

        plt.tight_layout()
        plt.show()


    # def show_assingn_state(self,assingned_shift):

    #     plt.style.use("ggplot")

    #     fig, axs = plt.subplots(1, 1, figsize=(10, 14))
    #     fig.tight_layout(pad=6.0)

    #     assingn_state=[]
    #     for i in range(len(self.data["shift_patterns"])):
    #         if assingned_shift[i]<=0:continue
    #         tmp=[]
    #         for time in self.data["shift_patterns"][i]:
    #             if time==1:tmp.append(assingned_shift[i])
    #             else :tmp.append(0)
    #         assingn_state.append(tmp)

    #     print(f"a_s:{assingn_state}")

        #  # 4. 実際の割り当てられたシフトパターンのオーバーレイ
        # shift_assignment_img = axs[0].imshow(assingned_shift, cmap=ListedColormap(["white", "blue"]), aspect="auto", alpha=0.5)

        # axs[0].set_title("Actual Assigned Shifts on Employee Availability", fontsize=14, fontweight="bold")
        # axs[0].set_xlabel("Time Slot", fontsize=12)
        # axs[0].set_ylabel("Employee ID", fontsize=12)

        # # グリッドやラベル設定
        # axs[0].set_xticks(np.arange(np.array(assingned_shift).shape[1]), minor=False)
        # axs[0].set_yticks(np.arange(np.array(assingned_shift).shape[0]), minor=False)
        # axs[0].set_xticks(np.arange(-0.5, np.array(assingned_shift).shape[1]), minor=True)
        # axs[0].set_yticks(np.arange(-0.5, np.array(assingned_shift).shape[0]), minor=True)
        # axs[0].set_xticklabels(np.arange(1, np.array(assingned_shift).shape[1] + 1))
        # axs[0].set_yticklabels(np.arange(1, np.array(assingned_shift).shape[0] + 1))
        # axs[0].grid(which="both", color="gray", linestyle="--", linewidth=0.5)
        # axs[0].grid(which="major", color="none")

        # # レジェンドの作成
        # from matplotlib.lines import Line2D
        # legend_elements = [
        #     Line2D([0], [0], color="blue", lw=4, label="Assigned Shifts"),
        #     Line2D([0], [0], color="green", lw=4, label="Preferences"),
        #     Line2D([0], [0], color="red", lw=4, label="Unavailable Slots")
        # ]
        # axs[0].legend(handles=legend_elements, loc="upper right", fontsize=10)

        # plt.show()

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
        data=np.array(data)
        data_sum = data[:,0] + data[:,1]

        plt.figure(figsize=(10, 6))
        
        # 各行のデータをプロット（合計値をカラーマップで指定）
        plt.scatter(data[:,0],data[:,1], c=data_sum, cmap='plasma', alpha=0.7)

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


