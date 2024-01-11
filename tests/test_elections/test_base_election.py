"""
Tests for elections.base_election
"""
# pylint: skip-file

from unittest.mock import patch

import pytest

import elections
import election_data


class ConcreteElection(elections.Election):
    @property
    def election_type(self):
        return "test_election_type"

    def _calculate_results(self):
        return {"test_result": 1}


class ConcreteElectionData(election_data.ElectionData):

    def get_elections(self):
        pass

    def get_regions(self, election_name):
        pass

    def get_vote_data(self, election_name, region=None, ignore_other=False):
        pass


@pytest.fixture()
def test_election():
    yield ConcreteElection(election_name="test_name",
                           vote_data=ConcreteElectionData())


def test_calculate_all(test_election):
    with (patch.object(test_election, "calculate_results") as results,
          patch.object(test_election, "calculate_coalitions") as coalitions
          ):
        test_election.calculate_all()
        results.assert_called_once()
        coalitions.assert_called_once()


def test_calculate_results_return_value(test_election):
    expected_results = {"test_result": 1}

    test_election.calculate_results()

    actual_results = test_election.results
    assert actual_results == expected_results


def test_results_raises_error_when_not_calculated(test_election):
    with pytest.raises(elections.NotCalculatedError):
        _ = test_election.results


def test_no_error_after_calculate_results(test_election):
    test_election.calculate_results()
    _ = test_election.results


def test_calculate_coalitions_raises_error_without_results(test_election):
    with pytest.raises(elections.NotCalculatedError):
        test_election.calculate_coalitions()


def test_coalitions_raises_error_when_not_calculated(test_election):
    with pytest.raises(elections.NotCalculatedError):
        _ = test_election.coalitions


def test_no_error_after_calculate_coalitions(test_election):
    test_election.calculate_results()
    test_election.calculate_coalitions()
    _ = test_election.coalitions


def test_coalitions_typical_election(test_election):
    parties = {"party1": 1,
               "party2": 1,
               "party3": 3,
               "party4": 4}
    expected_coalitions = [['party4', 'party3'],
                           ['party4', 'party1'],
                           ['party4', 'party2'],
                           ['party3', 'party1', 'party2']]

    with patch.object(test_election, "_calculate_results", new=lambda: parties):
        test_election.calculate_results()
    test_election.calculate_coalitions()

    actual_coalitions = test_election.coalitions
    assert actual_coalitions == expected_coalitions


def test_coalitions_single_winner(test_election):
    parties = {"party1": 10,
               "party2": 1,
               "party3": 1,
               "party4": 1}
    expected_coalitions = [['party1']]

    with patch.object(test_election, "_calculate_results", new=lambda: parties):
        test_election.calculate_results()
    test_election.calculate_coalitions()

    actual_coalitions = test_election.coalitions
    assert actual_coalitions == expected_coalitions


def test_coalitions_no_viable_coalition(test_election):
    parties = {"party1": 1,
               "party2": 1,
               "party3": 1,
               "party4": 1,
               "party5": 1,
               "party6": 1,
               "party7": 1}
    expected_coalitions = []

    with patch.object(test_election, "_calculate_results", new=lambda: parties):
        test_election.calculate_results()
    test_election.calculate_coalitions()

    actual_coalitions = test_election.coalitions
    assert actual_coalitions == expected_coalitions


def test_sort_results(test_election):
    parties = {"party1": 2,
               "party2": 1,
               "party3": 4,
               "Other": 7,
               }
    expected_sorting = ['party3', 'party1', 'party2', 'Other']

    actual_sorting = list(test_election.sort_results(parties))
    assert actual_sorting == expected_sorting
