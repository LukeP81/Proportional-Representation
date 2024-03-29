"""
Tests for election_data.database
"""
# pylint: skip-file

from contextlib import contextmanager
from unittest.mock import MagicMock, patch
import sqlite3

import numpy as np
import pytest

import election_data


@contextmanager
def mock_connection(dummy_parameter):
    _ = dummy_parameter  # to avoid flagging linters
    conn = sqlite3.connect(":memory:")
    cursor = conn.cursor()

    cursor.execute(
        "CREATE TABLE election1"
        "(\"Votes-PartyA\" INT, \"Votes-PartyB\" INT, \"Country/Region\" TEXT);")
    cursor.execute("INSERT INTO election1 VALUES (10, 20, 'Region1');")
    cursor.execute("INSERT INTO election1 VALUES (30, 40, 'Region2');")

    cursor.execute(
        "CREATE TABLE election2"
        "(\"Votes-PartyC\" INT, \"Votes-Other\" INT, \"Country/Region\" TEXT);")
    cursor.execute("INSERT INTO election2 VALUES (50, 60, 'Region3');")
    cursor.execute("INSERT INTO election2 VALUES (70, 80, 'Region2');")

    conn.commit()
    yield cursor
    cursor.close()
    conn.close()


@patch('sqlite3.connect')
def test_connect_to_database(mock_connect):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_connect.return_value = mock_conn

    expected_cursor = mock_cursor
    test_instance = election_data.DatabaseElectionData("test_path")
    with test_instance._connect_to_database() as actual_cursor:
        assert actual_cursor == expected_cursor

    mock_connect.assert_called_once_with(database=test_instance.database_path)
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()


def test_get_elections():
    expected_elections = ["election1", "election2"]

    with patch.object(target=election_data.DatabaseElectionData,
                      attribute="_connect_to_database",
                      new=mock_connection):
        test_instance = election_data.DatabaseElectionData("")

        actual_elections = test_instance.get_elections()
        assert actual_elections == expected_elections


@pytest.mark.parametrize("election, expected_regions",
                         [("election1", ['Region1', 'Region2']),
                          ("election2", ['Region3', 'Region2'])])
def test_get_regions(election, expected_regions):
    with patch.object(target=election_data.DatabaseElectionData,
                      attribute="_connect_to_database",
                      new=mock_connection):
        test_instance = election_data.DatabaseElectionData("")
        actual_regions = test_instance.get_regions(election_name=election)
        assert actual_regions == expected_regions


def test_get_vote_data_no_params():
    expected_parties = ["PartyA", "PartyB"]
    expected_votes = np.array([[10, 20], [30, 40]], dtype=np.float64)

    with patch.object(target=election_data.DatabaseElectionData,
                      attribute="_connect_to_database", new=mock_connection):
        test_instance = election_data.DatabaseElectionData("")

        actual_parties, actual_votes = test_instance.get_vote_data(
            election_name="election1")

        assert actual_parties == expected_parties
        assert np.array_equal(actual_votes, expected_votes)


def test_get_vote_data_by_region_when_region_present():
    expected_parties = ["PartyA", "PartyB"]
    expected_votes = np.array([[10, 20]], dtype=np.float64)

    with patch.object(target=election_data.DatabaseElectionData,
                      attribute="_connect_to_database", new=mock_connection):
        test_instance = election_data.DatabaseElectionData("mocked_path")

        actual_parties, actual_votes = test_instance.get_vote_data(
            election_name="election1", region="Region1")

        assert actual_parties == expected_parties
        assert np.array_equal(actual_votes, expected_votes)


def test_get_vote_data_by_region_when_region_not_present():
    expected_parties = []
    expected_votes = np.array([], dtype=np.float64)

    with patch.object(target=election_data.DatabaseElectionData,
                      attribute="_connect_to_database", new=mock_connection):
        test_instance = election_data.DatabaseElectionData("mocked_path")

        actual_parties, actual_votes = test_instance.get_vote_data(
            election_name="election1", region="Does not exist")

        assert actual_parties == expected_parties
        assert np.array_equal(actual_votes, expected_votes)


def test_get_vote_data_ignore_other_when_other_present():
    expected_parties = ["PartyC"]
    expected_votes = np.array([[50], [70]], dtype=np.float64)

    with patch.object(target=election_data.DatabaseElectionData,
                      attribute="_connect_to_database", new=mock_connection):
        test_instance = election_data.DatabaseElectionData("mocked_path")

        actual_parties, actual_votes = test_instance.get_vote_data(
            election_name="election2", ignore_other=True)

        assert actual_parties == expected_parties
        assert np.array_equal(actual_votes, expected_votes)


def test_get_vote_data_ignore_other_when_other_not_present():
    expected_parties = ["PartyA", "PartyB"]
    expected_votes = np.array([[10, 20], [30, 40]], dtype=np.float64)

    with patch.object(target=election_data.DatabaseElectionData,
                      attribute="_connect_to_database", new=mock_connection):
        test_instance = election_data.DatabaseElectionData("mocked_path")

        actual_parties, actual_votes = test_instance.get_vote_data(
            election_name="election1", ignore_other=True)

        assert actual_parties == expected_parties
        assert np.array_equal(actual_votes, expected_votes)
