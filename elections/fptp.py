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

from elections.base import Election
import election_data


class FirstPastThePost(Election):
    """
    Class representing a First Past The Post election.

    Attributes:
    - election_name (str): The name/year of the election.
    - maximum_coalition_size (int): The max number of parties in a coalition.

    Properties:
    - election_type (str): Property representing the type of the election.

    Methods:
    - _calculate_results: Calculates the FPTP election results.
    """

    def __init__(
            self,
            election_name: str,
            vote_data: election_data.DatabaseElectionData,
            maximum_coalition_size: int
    ):
        """
        :param election_name: The name or year of the election.
        :type election_name: str
        :param vote_data:
        :type vote_data:
        :param maximum_coalition_size: The max number of parties in a coalition.
        :type maximum_coalition_size: int
        """

        super().__init__(election_name, vote_data, maximum_coalition_size)

    @property
    def election_type(self) -> str:
        return "First Past The Post"

    def _calculate_results(self) -> Dict[str, int]:
        """
        Calculates the FPTP election results based on the specified parameters.

        :return: A dictionary mapping party names to the number of seats won.
        :rtype: Dict[str, int]
        """

        parties, votes = self.vote_data.get_vote_data(
            election_name=self.election_name)
        max_vote_counts = votes.max(axis=1, initial=0)
        winning_party_flags = np.array(votes == max_vote_counts[:, np.newaxis])
        parties_seats = dict(zip(parties, winning_party_flags.sum(axis=0)))
        return self.sort_results(parties_seats)
