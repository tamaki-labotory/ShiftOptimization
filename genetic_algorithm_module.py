from __future__ import annotations

from typing import TypeVar, List, Dict
from random import choices, random, randrange, shuffle
from heapq import nlargest
from abc import ABC, abstractmethod
from copy import deepcopy
from datetime import datetime
from solver.graph import ShiftDataVisualizer
from matplotlib import pyplot as plt

class Chromosome(ABC):
    """
    染色体（遺伝的アルゴリズムの要素1つ分）を扱う抽象クラス。
    """

    @abstractmethod
    def get_fitness1(self) -> float:
        """
        対象の問題に対する染色体の優秀さを取得する評価関数Y用の
        抽象メソッド。

        Returns
        -------
        fitness : float
            対象の問題に対する染色体の優秀さの値。高いほど問題に
            適した染色体となる。
            遺伝的アルゴリズムの終了判定などにも使用される。
        """
        ...
    def get_fitness2(self) -> float:
        """
        対象の問題に対する染色体の優秀さを取得する評価関数Y用の
        抽象メソッド。

        Returns
        -------
        fitness : float
            対象の問題に対する染色体の優秀さの値。高いほど問題に
            適した染色体となる。
            遺伝的アルゴリズムの終了判定などにも使用される。
        """
        ...

    @classmethod
    @abstractmethod
    def make_random_instance(cls) -> Chromosome:
        """
        ランダムな特徴（属性値）を持ったインスタンスを生成する
        抽象メソッド。

        Returns
        -------
        instance : Chromosome
            生成されたインスタンス。
        """
        ...

    @abstractmethod
    def mutate(self) -> None:
        """
        染色体を（突然）変異させる処理の抽象メソッド。
        インスタンスの属性などのランダムな別値の設定などが実行される。
        """
        ...

    @abstractmethod
    def exec_crossover(self, other: Chromosome) -> List[Chromosome]:
        """
        引数に指定された別の個体を参照し交叉を実行する。

        Parameters
        ----------
        other : Chromosome
            交叉で利用する別の個体。

        Returns
        -------
        result_chromosomes : list of Chromosome
            交叉実行後に生成された2つの個体（染色体）。
        """
        ...

    def __lt__(self, other: Chromosome) -> bool:
        """
        個体間の比較で利用する、評価関数の値の小なり比較用の関数。

        Parameters
        ----------
        other : Chromosome
            比較対象の他の個体。

        Returns
        -------
        result_bool : bool
            小なり条件を満たすかどうかの真偽値。
        """
        return self.get_fitness1() < other.get_fitness1() and self.get_fitness2() < other.get_fitness2()




C = TypeVar('C', bound=Chromosome)

class GeneticAlgorithm:

    SelectionType = int
    SELECTION_TYPE_ROULETTE_WHEEL: SelectionType = 1
    SELECTION_TYPE_TOURNAMENT: SelectionType = 2

    def __init__(
            self, 
            initial_population1: List[C],
            initial_population2: List[C],
            threshold: float,
            max_generations: int, mutation_probability: float,
            crossover_probability: float,
            selection_type: SelectionType) -> None:
        """
        遺伝的アルゴリズムを扱うクラス。

        Parameters
        ----------
        initial_population : list of Chromosome
            initial_population1とinitial_population2を統合したもの
        initial_population1 : list of Chromosome
            最初の世代の個体群（目的関数1用）。
        initial_population : list of Chromosome
            最初の世代の個体群（目的関数2用）。
        threshold : float
            問題解決の判定で利用するしきい値。この値を超える個体が
            発生した時点で計算が終了する。
        max_generations : int
            アルゴリズムで実行する最大世代数。
        mutation_probability : float
            変異確率（0.0～1.0）。
        crossover_probability : float
            交叉確率（0.0～1.0）。
        selection_type : int
            選択方式。以下のいずれかの定数値を指定する。
            - SELECTION_TYPE_ROULETTE_WHEEL
            - SELECTION_TYPE_TOURNAMENT
        """
        self._population: List[Chromosome] = initial_population1+initial_population2
        self._population1: List[Chromosome] = initial_population1
        self._population2: List[Chromosome] = initial_population2
        self._threshold: float = threshold
        self._max_generations: int = max_generations
        self._mutation_probability: float = mutation_probability
        self._crossover_probability: float = crossover_probability
        self._selection_type: int = selection_type

    def _exec_roulette_wheel_selection(self,index) -> List[Chromosome]:
        """
        ルーレット選択を行い、交叉などで利用する2つの個体（染色体）を
        取得する。

        Returns
        -------
        selected_chromosomes : list of Chromosome
            選択された2つの個体（染色体）を格納したリスト。選択処理は評価関数
            （fitnessメソッド）による重みが設定された状態でランダムに抽出される。

        Notes
        -----
        評価関数の結果の値が負になる問題には利用できない。
        """
        if index==1:
            weights: List[float] = [
                chromosome.get_fitness1() for chromosome in self._population1]
            
            min_weight = min(weights)
            weights = [w - min_weight for w in weights]

            selected_chromosomes: List[Chromosome] = choices(
                self._population1, weights=weights, k=2)
            return selected_chromosomes
        if index==2:
            weights: List[float] = [
                chromosome.get_fitness2() for chromosome in self._population2]
            
            min_weight = min(weights)
            weights = [w - min_weight for w in weights]

            selected_chromosomes: List[Chromosome] = choices(
                self._population2, weights=weights, k=2)
            return selected_chromosomes

    def _exec_tournament_selection(self,index) -> List[Chromosome]:
        """
        トーナメント選択を行い、交叉などで利用するための2つの個体
        （染色体）を取得する。

        Returns
        -------
        selected_chromosomes : list of Chromosome
            選択された2つの個体（染色体）を格納したリスト。トーナメント
            用に引数で指定された件数分抽出された中から上位の2つの個体が
            設定される。
        """
        participants_num: int = len(self._population)
        if index==1:  
            participants: List[Chromosome] = choices(self._population1, k=participants_num)
            selected_chromosomes: List[Chromosome] = nlargest(n=20, iterable=participants,key=lambda participant: participant.get_fitness1())
            return selected_chromosomes
        if index==2:
            participants: List[Chromosome] = choices(self._population2, k=participants_num)
            selected_chromosomes: List[Chromosome] = nlargest(n=20, iterable=participants,key=lambda participant: participant.get_fitness2())
            return selected_chromosomes
        if index==3:
            participants: List[Chromosome] = choices(self._population, k=participants_num)
            selected_chromosomes: List[Chromosome] = nlargest(n=20, iterable=participants,key=lambda participant: participant.get_fitness1()+participant.get_fitness2())
            return selected_chromosomes

    def _to_next_generation(self) -> None:
        """
        次世代の個体（染色体）を生成し、個体群の属性値を生成した
        次世代の個体群で置換する。
        """
        new_population: List[Chromosome] = []

        # 元の個体群の件数が奇数件数の場合を加味して件数の比較は等値ではなく
        # 小なりの条件で判定する。
        parent1 : List[Chromosome] = self._get_parents_by_selection_type(1)
        parent2 : List[Chromosome] = self._get_parents_by_selection_type(2)
        parent1_and_2 : List[Chromosome] = self._get_parents_by_selection_type(3)
        parents=parent1+parent2+parent1_and_2
        new_population.extend(parents)
        while len(new_population) < len(self._population):
            selected_parents=choices(parents, k=2)
            next_generation_chromosomes: List[Chromosome] = self._get_next_generation_chromosomes(parents=selected_parents)
            new_population.extend(next_generation_chromosomes)

        # 元のリストよりも件数が多い場合は1件ずつ、リストから取り除いてリストの件数を元のリストと一致させる。
        while len(new_population) > len(self._population):
            del new_population[-1]

        shuffle(new_population)
        mid=(len(new_population)-1)//2

        self._population = new_population
        self._population1 = new_population[:mid]
        self._population2 = new_population[mid:]

    def _get_next_generation_chromosomes(
            self, parents: List[Chromosome]) -> List[Chromosome]:
        """
        算出された親の2つの個体のリストから、次世代として扱う
        2つの個体群のリストを取得する。
        一定確率で交叉や変異させ、確率を満たさない場合には引数の値が
        そのまま次世代として設定される。

        Parameters
        ----------
        parents : list of Chromosome
            算出された親の2つの個体のリスト

        Returns
        -------
        next_generation_chromosomes : list of Chromosome
            次世代として設定される、2つの個体を格納したリスト。
        """
        random_val: float = random()
        next_generation_chromosomes: List[Chromosome] = parents
        if random_val < self._crossover_probability:
            next_generation_chromosomes = parents[0].exec_crossover(
                other=parents[1])

        random_val = random()
        if random_val < self._mutation_probability:
            for chromosome in next_generation_chromosomes:
                chromosome.mutate()
        return next_generation_chromosomes

    def _get_parents_by_selection_type(self,index) -> List[Chromosome]:
        """
        選択方式に応じた親の2つの個体（染色体）のリストを取得する。

        Returns
        -------
        parents : list of Chromosome
            取得された親の2つの個体（染色体）のリスト。

        Raises
        ------
        ValueError
            対応していない選択方式が指定された場合。
        """
        if self._selection_type == self.SELECTION_TYPE_ROULETTE_WHEEL:
            parents: List[Chromosome] = self._exec_roulette_wheel_selection(index)
        elif self._selection_type == self.SELECTION_TYPE_TOURNAMENT:
            parents = self._exec_tournament_selection(index)
        else:
            raise ValueError(
                '対応していない選択方式が指定されています : %s'
                % self._selection_type)
        return parents


    def run_algorithm(self) -> Chromosome:
        """
        遺伝的アルゴリズムを実行し、実行結果の個体（染色体）のインスタンス
        を取得する。

        Returns
        -------
        betst_chromosome : Chromosome
            アルゴリズム実行結果の個体。評価関数でしきい値を超えた個体
            もしくはしきい値を超えない場合は指定された世代数に達した
            時点で一番評価関数の値が高い個体が設定される。
        """
        best_chromosome: Chromosome = deepcopy(self._get_best_chromosome_from_population())
        for generation_idx in range(self._max_generations):

            if best_chromosome.get_fitness1()+best_chromosome.get_fitness2() >= self._threshold:
                return best_chromosome

            self._to_next_generation()

            currrent_generation_best_chromosome: Chromosome = self._get_best_chromosome_from_population()
            current_gen_best_fitness: List[float] = [currrent_generation_best_chromosome.get_fitness1(),currrent_generation_best_chromosome.get_fitness2()]
            if best_chromosome.get_fitness1() + best_chromosome.get_fitness2() < current_gen_best_fitness[0] +current_gen_best_fitness[1]:
                best_chromosome = deepcopy(currrent_generation_best_chromosome)
                print(
                f'世代数 : {generation_idx}'
                f'　最良個体情報 : {best_chromosome}'
                )
        show_data_num_of_fitness1=[]
        show_data_num_of_fitness2=[]
        for i  in range(len(self._population)):
            if self._population[i].get_fitness1()>-1000 and self._population[i].get_fitness2()>-1000:
                show_data_num_of_fitness1.append(self._population[i].get_fitness1())
                show_data_num_of_fitness2.append(self._population[i].get_fitness2())
                print(f"パレート解:{self._population[i].__str__()}")

        #得られた解の表示
        sdv=ShiftDataVisualizer()
        show_data=[[show_data_num_of_fitness1[i],show_data_num_of_fitness2[i]] for i in range(len(show_data_num_of_fitness1))] 
        sdv.show_scatter_using_heat_map(show_data,"Shift Preference Fulfillment Rate(Objective1)","Shift Vacancy Rate(Objective2)","","Objective1+Objective2")
        
        return best_chromosome

    def _get_best_chromosome_from_population(self) -> Chromosome:
        """
        個体群のリストから、評価関数の値が一番高い個体（染色体）を
        取得する。

        Returns
        -------
        best_chromosome : Chromosome
            リスト内の評価関数の値が一番高い個体。
        """
        best_chromosome: Chromosome = self._population[0]
        for chromosome in self._population:
            if best_chromosome.get_fitness1()< chromosome.get_fitness1() and best_chromosome.get_fitness2() <chromosome.get_fitness2():
                best_chromosome = chromosome
        return best_chromosome

