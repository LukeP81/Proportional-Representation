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
"""

from collections import Counter
from typing import Dict, List
import heapq

import numpy as np

from elections.election_base import Election
from database_retriever import get_vote_data, get_regions


class ProportionalRepresentation(Election):
    """
    Class representing a Proportional Representation election.

    Attributes:
    - election_name (str): The name of the election.
    - maximum_coalition_size (int): The max number of parties in a coalition.
    - pr_by_region (bool): Whether the PR is calculated by region.
    - ignore_other (bool): Whether to ignore "Other" in calculations.

    Properties:
    - election_type (str): Property representing the type of the election.

    Methods:
    - _calculate_results: Calculates the PR election results based on the
        specified parameters.
    - _compute_seats_by_pr: Computes the number of seats each party obtains in a
        PR election using the D'Hondt method.
    """

    def __init__(
            self,
            election_name: str,
            maximum_coalition_size: int,
            pr_by_region: bool = True,
            ignore_other: bool = True
    ):
        """
        :param election_name: The name of the election.
        :type election_name: str
        :param maximum_coalition_size: The max number of parties in a coalition.
        :type maximum_coalition_size: int
        :param pr_by_region: Whether the PR is calculated by region.
        :type pr_by_region: bool
        :param ignore_other: Whether to ignore "Other" in calculations.
        :type ignore_other: bool
        """

        super().__init__(election_name, maximum_coalition_size)
        self.pr_by_region = pr_by_region
        self.ignore_other = ignore_other

    @property
    def election_type(self) -> str:
        """
        Property representing the type of the election.
        """
        return "Proportional Representation"

    def _calculate_results(self) -> Dict[str, int]:
        """
        Calculates the PR election results based on the specified parameters.
        """
        if not self.pr_by_region:
            parties, votes = get_vote_data(table_name=self.election_name,
                                           ignore_other=self.ignore_other)
            results = self._compute_seats_by_pr(parties=parties, votes=votes)
            return self.sort_results(results=results)

        regions = get_regions(table_name=self.election_name)
        region_seats = []
        for region in regions:
            parties, votes = get_vote_data(table_name=self.election_name,
                                           region=region,
                                           ignore_other=self.ignore_other)
            region_seats.append(self._compute_seats_by_pr(parties=parties,
                                                          votes=votes))
        return self.sort_results(results=dict(
            sum([Counter(region) for region in region_seats], Counter())))

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
