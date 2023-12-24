from abc import ABC, abstractmethod
from collections import OrderedDict
from typing import Dict

import numpy as np


class Election(ABC):
    def __init__(self, year, maximum_coalition_size):
        self.year = year
        self.maximum_coalition_size = maximum_coalition_size

        self._results = None
        self._results_calculated = False

        self._coalitions = None
        self._coalitions_calculated = False

    @property
    def results(self):
        if not self._results_calculated:
            raise ValueError(
                "Results not calculated. Call calculate_results first.")
        return self._results

    @property
    def coalitions(self):
        if not self._coalitions_calculated:
            raise ValueError(
                "Results not calculated. Call calculate_results first.")
        return self._coalitions

    def calculate_results(self):
        self._calculate_results()
        self._results_calculated = True

    @abstractmethod
    def _calculate_results(self) -> Dict[str, int]:
        pass

    @staticmethod
    def sort_results(results):
        def sort_parties(item):
            return item[1] if item[0] != "Other" else -1

        return OrderedDict(
            sorted(results.items(), key=sort_parties, reverse=True))

    def find_valid_coalitions(self):
        total = sum(self.results.values())

        sorted_list = sorted(
            [(seats, party) for party, seats in self.results.items()],
            key=lambda x: x[0],
            reverse=True)

        seat_target = np.ceil((total + 1) / 2)
        valid_coalitions = self._find_valid_coalitions_recursive(
            remaining_parties=sorted_list,
            seat_target=seat_target)

        return valid_coalitions

    def _find_valid_coalitions_recursive(self,
                                         remaining_parties,
                                         seat_target,
                                         current_selection=None
                                         ):
        if current_selection is None:
            current_selection = []

        if sum(item[0] for item in current_selection) >= seat_target:
            return [[item[1] for item in current_selection]]

        if len(current_selection) + 1 > self.maximum_coalition_size:
            return []

        valid_coalitions = []
        for index, item in enumerate(remaining_parties):
            next_coalition = self._find_valid_coalitions_recursive(
                remaining_parties=remaining_parties[index + 1:],
                seat_target=seat_target,
                current_selection=current_selection + [item])
            valid_coalitions.extend(next_coalition)

        return valid_coalitions
