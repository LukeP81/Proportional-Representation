from typing import Dict

import numpy as np

from database_retriever import get_vote_data
from elections.election_base import Election


class FirstPastThePost(Election):
    def __init__(
            self,
            election_name: str,
            maximum_coalition_size: int
    ):
        """
        :param election_name: The name or year of the election.
        :type election_name: str
        :param maximum_coalition_size: The max number of parties in a coalition.
        :type maximum_coalition_size: int
        """
        super().__init__(election_name, maximum_coalition_size)

    @property
    def election_type(self) -> str:
        """
        Property representing the type of the election.
        """
        return "First Past The Post"

    def _calculate_results(self) -> Dict[str, int]:
        """
        Calculates the FPTP election results based on the specified parameters.
        """
        parties, votes = get_vote_data(table_name=self.election_name)
        max_vote_counts = votes.max(axis=1, initial=0)
        winning_party_flags = np.array(votes == max_vote_counts[:, np.newaxis])
        parties_seats = dict(zip(parties, winning_party_flags.sum(axis=0)))
        return self.sort_results(parties_seats)
