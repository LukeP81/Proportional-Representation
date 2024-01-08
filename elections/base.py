"""
Election Base Module

This module defines an abstract base class for representing elections,
providing methods for calculating election results and valid coalitions.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional
import math

import election_data


class NotCalculatedError(BaseException):
    """
    Custom exception raised when attempting to access election results or
    coalitions before they have been calculated.
    """


class Election(ABC):
    """
    Abstract base class representing an election.

    Attributes:
    - election_name (str): The name of the election.
    - maximum_coalition_size (int): The max number of parties in a coalition.

    Properties:
    - election_type (str): Abstract property representing the type
      of the election.
    - results (dict): Property that returns the election results.
    - coalitions (list): Property that returns the valid coalitions formed based
      on election results.

    Methods:
    - calculate_results: Calculates the election results and marks
      them as calculated.
    - _calculate_results: Abstract private method to be implemented by
      subclasses for calculating election results.
    - calculate_coalitions: Calculates the valid coalitions based on election
      results and marks them as calculated.
    - _calculate_coalitions: Private method to calculate valid coalitions
      based on election results.
    - _find_valid_coalitions_recursive: Recursive helper method to find valid
      coalitions from election results.
    - sort_results: Static method to sort election results in
      a specific order.
    """

    def __init__(
            self,
            election_name: str,
            vote_data: election_data.ElectionData,
            maximum_coalition_size: int = 3
    ):
        """
        :param election_name: The name of the election.
        :type election_name: str
        :param maximum_coalition_size: The max number of parties in a coalition.
        :type maximum_coalition_size: int
        """

        self.election_name = election_name
        self.vote_data = vote_data
        self.maximum_coalition_size = maximum_coalition_size

        self._results: Dict[str, int] = {}
        self._results_calculated = False

        self._coalitions: List[List[str]] = []
        self._coalitions_calculated = False

    @property
    @abstractmethod
    def election_type(self) -> str:
        """
        Property representing the type of the election.

        :return: The type of the election.
        :rtype: str
        """

    @property
    def results(self) -> dict:
        """
        Property that returns the election results.

        :return: A dictionary containing party names as keys and their
                 corresponding seat counts as values.
        :rtype: Dict[str, int]
        :raises NotCalculatedError: If results have not been calculated.
        """

        if not self._results_calculated:
            raise NotCalculatedError(
                "Results not calculated. Call calculate_results first.")
        return self._results

    @property
    def coalitions(self) -> list:
        """
        Property that returns the valid coalitions formed based on election
        results. It is possible that this can be just a single winner.

        :return: A list of lists where each inner list represents a
                 coalition of parties.
        :rtype: List[List[str]]
        :raises NotCalculatedError: If results have not been calculated.
        """

        if not self._coalitions_calculated:
            raise NotCalculatedError(
                "Results not calculated. Call calculate_results first.")
        return self._coalitions

    def calculate_all(self) -> None:
        """
        Calls all calculates methods.
        """

        self.calculate_results()
        self.calculate_coalitions()

    def calculate_results(self) -> None:
        """
        Calculates the election results and marks them as calculated.
        """

        results = self._calculate_results()
        self._results = results
        self._results_calculated = True

    @abstractmethod
    def _calculate_results(self) -> Dict[str, int]:
        """
        Abstract private method to be implemented by subclasses
        for calculating election results.

        :return: A dictionary containing party names as keys and their
                 corresponding seat counts as values.
        :rtype: Dict[str, int]
        """

    def calculate_coalitions(self) -> None:
        """
        Calculates the valid coalitions based on election results and
        marks them as calculated.
        """

        if not self._results_calculated:
            raise NotCalculatedError(
                "Results not calculated. Call calculate_results first.")

        coalitions = self._calculate_coalitions()
        self._coalitions = coalitions
        self._coalitions_calculated = True

    def _calculate_coalitions(self) -> List[List[str]]:
        """
        Method to calculate valid coalitions based on election results.

        :return: A list of valid coalitions, represented as a list of party names.
                 Returns an empty list if no valid coalitions are found.
        :rtype: List[List[str]]
        """

        total = sum(self.results.values())

        sorted_list = sorted(
            [(seats, party) for party, seats in self.results.items()],
            key=lambda x: x[0],
            reverse=True)

        seat_target = math.ceil((total + 1) / 2)

        valid_coalitions = self._find_valid_coalitions_recursive(
            remaining_parties=sorted_list,
            seat_target=seat_target)

        return valid_coalitions if valid_coalitions else []

    def _find_valid_coalitions_recursive(
            self,
            remaining_parties: list,
            seat_target: int,
            current_selection: Optional[list] = None
    ) -> List[List[str]]:
        """
        Recursive helper method to find valid coalitions from election results.
        Base case 1: coalition of valid size -> return the coalition
        Base case 2: coalition would be too large -> return empty list
        Recursive step: loop through remaining parties and find all valid
                        combinations with current_selection

        :param remaining_parties: List of remaining parties to consider
        :type remaining_parties: List[tuple]
        :param seat_target: The target number of seats to achieve in a coalition.
        :type seat_target: int
        :param current_selection: Current selection of parties.
        :type current_selection: Optional[List[tuple]]
        :return: List of valid coalitions.
        :rtype: List[List[str]]
        """

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

    @staticmethod
    def sort_results(
            results: dict
    ) -> dict:
        """
        Static method to sort election results in a specific order.

        :param results: The unsorted election results.
        :type results: Dict[str, int]
        :return: The sorted election results.
        :rtype: Dict[str, int]
        """

        def sort_parties(item: tuple) -> int:
            return item[1] if item[0] != "Other" else -1

        return dict(sorted(results.items(), key=sort_parties, reverse=True))
