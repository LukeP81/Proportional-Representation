"""
Tests for elections.fptp
"""
# pylint: skip-file

from unittest.mock import patch

import numpy as np
import pytest

import elections
import election_data


class ConcreteElectionData(election_data.ElectionData):
    def get_elections(self):
        """Blank implementation of abstract method"""

    def get_regions(self, election_name):
        """Blank implementation of abstract method"""

    def get_vote_data(self, election_name, region=None, ignore_other=False):
        """Blank implementation of abstract method"""


@pytest.fixture()
def test_election():
    yield elections.FirstPastThePost(
        election_name="test_name",
        data_retriever=ConcreteElectionData())


def test_election_type(test_election):
    expected_election_type = "First Past The Post"
    actual_election_type = test_election.election_type
    assert actual_election_type == expected_election_type


def test_calculate_results(test_election):
    expected_results = {"Party2": 3, "Party3": 2, "Party1": 1, }
    voting_data = (["Party1", "Party2", "Party3"],
                   np.array([[99, 1, 1],
                             [1, 99, 1],
                             [1, 1, 99],
                             [1, 99, 1],
                             [1, 1, 99],
                             [1, 99, 1]],
                            dtype=np.float64))

    with patch.object(ConcreteElectionData,
                      "get_vote_data") as mock_get_vote_data:
        mock_get_vote_data.return_value = voting_data
        test_election.calculate_results()

        actual_results = test_election.results
        assert list(actual_results.items()) == list(expected_results.items())


def test_calculate_results_draw_does_not_duplicate_seat(test_election):
    expected_seat_amount = 2
    voting_data = (["Party1", "Party2"],
                   np.array([[99, 1],
                             [99, 99]],
                            dtype=np.float64))

    with patch.object(ConcreteElectionData,
                      "get_vote_data") as mock_get_vote_data:
        mock_get_vote_data.return_value = voting_data
        test_election.calculate_results()

        actual_seat_amount = sum(test_election.results.values())
        assert actual_seat_amount == expected_seat_amount
