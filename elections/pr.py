"""
Proportional Representation Election Module

This module defines the ProportionalRepresentation class, a subclass of the
Election abstract base class.
The ProportionalRepresentation class represents an election using the
Proportional Representation voting system, where seats are allocated to parties
based on their proportion of the vote. In particular, it uses the D'Hondt
method which works by assigning seats based on the party that will have the most
votes per seat for each consecutive seat awarded, for more detail see:
https://en.wikipedia.org/wiki/D%27Hondt_method

Enumerations:
- MethodForPR: Defines different methods for Proportional Representation.
"""

from collections import Counter
from enum import Enum
from typing import Dict, List
import heapq

import numpy as np

from elections.base_election import Election
import election_data


class MethodForPR(Enum):
    """
    Enumeration defining different methods for Proportional Representation.
    """

    BY_REGION = "By Region"
    ENTIRE_ELECTORATE = "Entire Electorate"


class ProportionalRepresentation(Election):
    """
    Class representing a Proportional Representation election.

    Attributes:
    - pr_method (MethodForPR.BY_REGION): Method for the PR calculation.
    - ignore_other (bool): Whether to ignore "Other" in calculations.

    Methods:
    - _calculate_results: Calculates the PR election results based on the
        specified parameters.
    - _compute_seats_by_pr: Computes the number of seats each party obtains in a
        PR election using the D'Hondt method.
    - _calculate_entire_electorate: Calculates results for the entire electorate.
    - _calculate_by_region: Calculates results by individual regions.
    """

    def __init__(
            self,
            election_name: str,
            data_retriever: election_data.ElectionData,
            maximum_coalition_size: int = 3,
            pr_method: MethodForPR = MethodForPR.BY_REGION,
            ignore_other: bool = True
    ):
        """
        :param election_name: The name of the election.
        :type election_name: str
        :param data_retriever: The object that will handle retrieving election
        data.
        :type data_retriever: election_data.ElectionData
        :param maximum_coalition_size: The max number of parties in a coalition.
        :type maximum_coalition_size: int
        :param pr_method: How the PR is calculated.
        :type pr_method: bool
        :param ignore_other: Whether to ignore "Other" in calculations.
        :type ignore_other: bool
        """

        super().__init__(election_name, data_retriever, maximum_coalition_size)
        self.pr_method = pr_method
        self.ignore_other = ignore_other

    @property
    def election_type(self) -> str:
        return "Proportional Representation"

    @staticmethod
    def _compute_seats_by_pr(
            parties: List[str],
            votes: np.ndarray
    ) -> Dict[str, int]:
        """
        Computes the number of seats each party obtains in a PR election.
        Uses the D'Hondt method for assigning seats.

        :param parties: List of party names.
        :type parties: list
        :param votes: 2D array representing the votes received by
                      each party in each constituency.
        :type votes: np.ndarray
        :return: A dictionary containing party names as keys and their
                 corresponding seat counts as values.
        :rtype: Dict[str, int]
        """

        total_seats = np.shape(votes)[0]
        party_totals = np.sum(votes, axis=0)

        obtained_seats = [0] * len(parties)
        parties_min_heap = [(-total_vote, party) for party, total_vote in
                            enumerate(party_totals)]
        heapq.heapify(parties_min_heap)
        for _ in range(total_seats):
            votes_per_seat, party = heapq.heappop(parties_min_heap)
            obtained_seats[party] += 1
            votes_per_seat = -party_totals[party] / (obtained_seats[party] + 1)
            heapq.heappush(parties_min_heap, (votes_per_seat, party))

        return dict(zip(parties, obtained_seats))

    def _calculate_entire_electorate(self) -> Dict[str, int]:
        """
        Calculate PR election results for the entire electorate.

        :return: A dictionary containing party names as keys and their
                 corresponding seat counts as values.
        :rtype: Dict[str, int]
        """

        parties, votes = self.data_retriever.get_vote_data(
            election_name=self.election_name,
            ignore_other=self.ignore_other)
        results = self._compute_seats_by_pr(parties=parties, votes=votes)
        return self.sort_results(results=results)

    def _calculate_by_region(self) -> Dict[str, int]:
        """
        Calculate PR election results by individual regions.

        :return: A dictionary containing party names as keys and their
                 corresponding seat counts as values.
        :rtype: Dict[str, int]
        """

        regions = self.data_retriever.get_regions(
            election_name=self.election_name)
        region_seats = []
        for region in regions:
            parties, votes = self.data_retriever.get_vote_data(
                election_name=self.election_name,
                region=region,
                ignore_other=self.ignore_other)
            region_seats.append(self._compute_seats_by_pr(parties=parties,
                                                          votes=votes))
        return self.sort_results(results=dict(
            sum([Counter(region) for region in region_seats], Counter())))

    def _calculate_results(self) -> Dict[str, int]:
        """
        Calculates the PR election results based on the chosen method.
        """

        methods = {
            MethodForPR.BY_REGION: self._calculate_by_region,
            MethodForPR.ENTIRE_ELECTORATE: self._calculate_entire_electorate
        }
        return methods[self.pr_method]()
