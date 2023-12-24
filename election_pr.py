import numpy as np
import heapq
from collections import Counter

from election_base import Election
from database_retriever import get_vote_data, get_regions


class PR(Election):
    def __init__(self, year, maximum_coalition_size, pr_by_region, ignore_other):
        super().__init__(year, maximum_coalition_size)
        self.pr_by_region = pr_by_region
        self.ignore_other = ignore_other

    def _calculate_results(self):
        if not self.pr_by_region:
            parties, votes = get_vote_data(table_name=self.year,
                                           ignore_other=self.ignore_other)
            self._results = self.sort_results(
                self._compute_seats_by_pr(parties, votes, ))
            return
        regions = get_regions(table_name=self.year)
        region_seats = []
        for region in regions:
            parties, votes = get_vote_data(table_name=self.year, region=region,
                                           ignore_other=self.ignore_other)
            region_seats.append(self._compute_seats_by_pr(parties, votes))
        self._results = self.sort_results(
            dict(sum((Counter(region) for region in region_seats), Counter())))

    @staticmethod
    def _compute_seats_by_pr(parties, votes):

        total_seats = np.shape(votes)[0]
        total_votes_by_party = np.sum(votes, axis=0)

        obtained_seats = [0] * len(parties)
        parties_min_heap = [(-total_vote, party) for party, total_vote in
                            enumerate(total_votes_by_party)]
        heapq.heapify(parties_min_heap)
        for _ in range(total_seats):
            votes_per_seat, party = heapq.heappop(parties_min_heap)
            obtained_seats[party] += 1
            heapq.heappush(parties_min_heap, (
                -total_votes_by_party[party] / (obtained_seats[party] + 1),
                party))

        return {party: obtained_seat for party, obtained_seat in
                zip(parties, obtained_seats)}
