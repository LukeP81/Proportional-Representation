"""
First Past The Post Election Module

This module defines the FirstPastThePost class, a subclass of the
Election abstract base class.
The FirstPastThePost class represents an election using the
First Past The Post voting system, where the candidate or party with the
most votes in a constituency wins.
"""

from typing import Dict

import numpy as np

from elections.base_election import Election
import election_data


class FirstPastThePost(Election):
    """
    Class representing a First Past The Post election.

    Methods:
    - _calculate_results: Calculates the FPTP election results.
    """

    @property
    def election_type(self) -> str:
        return "First Past The Post"

    def _calculate_results(self) -> Dict[str, int]:
        """
        Calculates the FPTP election results based on the specified parameters.

        :return: A dictionary mapping party names to the number of seats won.
        :rtype: Dict[str, int]
        """

        parties, votes = self.data_retriever.get_vote_data(
            election_name=self.election_name)

        winning_party_indices = np.argmax(votes, axis=1)
        party_seat_counts = np.bincount(winning_party_indices,
                                        minlength=len(parties))

        parties_seats = dict(zip(parties, party_seat_counts))
        return self.sort_results(parties_seats)
