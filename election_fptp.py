import numpy as np

from election_base import Election
from database_retriever import get_vote_data


class FPTP(Election):
    def __init__(self, year, maximum_coalition_size):
        super().__init__(year, maximum_coalition_size)

    def _calculate_results(self):
        parties, votes = get_vote_data(self.year)
        max_values = votes.max(axis=1, initial=0)
        max_columns = np.array(votes == max_values[:, np.newaxis])
        column_counts = dict(
            zip(parties, max_columns.sum(axis=0)))
        self._results = self.sort_results(column_counts)
