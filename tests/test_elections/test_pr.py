"""
Tests for elections.pr
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
    yield elections.ProportionalRepresentation(
        election_name="test_name",
        data_retriever=ConcreteElectionData(),
        pr_method=elections.MethodForPR.BY_REGION)


@pytest.fixture()
def test_election_electorate():
    yield elections.ProportionalRepresentation(
        election_name="test_name",
        data_retriever=ConcreteElectionData(),
        pr_method=elections.MethodForPR.ENTIRE_ELECTORATE)


def test_election_type(test_election):
    expected_election_type = "Proportional Representation"
    actual_election_type = test_election.election_type
    assert actual_election_type == expected_election_type


def test_calculate_results_entire_electorate(test_election_electorate):
    expected_results = {"Party3": 3, "Party2": 2, "Party1": 1, }
    voting_data = (["Party1", "Party2", "Party3"],
                   np.array([[50, 100, 200],
                             [0, 0, 0],
                             [0, 0, 0],
                             [0, 0, 0],
                             [0, 0, 0],
                             [0, 0, 0]],
                            dtype=np.float64))

    with patch.object(test_election_electorate.data_retriever,
                      "get_vote_data") as mock_get_vote_data:
        mock_get_vote_data.return_value = voting_data
        test_election_electorate.calculate_results()

        actual_results = test_election_electorate.results
        assert list(actual_results.items()) == list(expected_results.items())


def test_calculate_results_by_region(test_election):
    def mock_get_vote_data_region(election_name, region, ignore_other):
        _ = election_name, ignore_other  # to avoid flagging linters

        if region == "Region1":
            return (["Party1", "Party2", "Party3"],
                    np.array([[999, 0, 0],
                              [0, 0, 0],
                              [0, 0, 0],
                              [0, 0, 0],
                              [0, 0, 0],
                              [0, 0, 0]],
                             dtype=np.float64))
        if region == "Region2":
            return (["Party2", "Party3", "Party4"],
                    np.array([[1, 1, 1],
                              [0, 0, 0],
                              [0, 0, 0]],
                             dtype=np.float64))

    expected_results = {"Party1": 6, "Party2": 1, "Party3": 1, "Party4": 1}

    with (patch.object(test_election.data_retriever,
                       "get_vote_data",
                       new=mock_get_vote_data_region),
          patch.object(test_election.data_retriever,
                       "get_regions") as mock_get_region):
        mock_get_region.return_value = ["Region1", "Region2"]
        test_election.calculate_results()

        actual_results = test_election.results
        assert list(actual_results.items()) == list(expected_results.items())
