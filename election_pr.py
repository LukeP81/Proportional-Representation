from typing import Dict, List

import numpy as np
import heapq
from collections import Counter

from election_base import Election
from database_retriever import get_vote_data, get_regions


class PR(Election):
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

        return {party: seats_obtained for party, seats_obtained in
                zip(parties, obtained_seats)}
