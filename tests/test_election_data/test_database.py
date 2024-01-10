"""
Tests for returned_data.database
"""

from contextlib import contextmanager
from unittest.mock import MagicMock, patch

import numpy as np
import pytest
import sqlite3

import election_data


@contextmanager
def mock_connection(dummy_parameter):
    """
    Mock connection context manager for SQLite database to replace the
    connection method (_connect_to_database)

    Parameters:
        dummy_parameter (Any): Only present to have the same signature.

    Yields:
        sqlite3.Cursor: A mock cursor for the database connection.
    """

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
    """
    Test the connection to the database.

    This test ensures that the DatabaseElectionData class establishes a connection
    to the database and returns the correct cursor when _connect_to_database is
    called. It also verifies that the connection and cursor are properly closed.
    """

    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_connect.return_value = mock_conn

    test_instance = election_data.DatabaseElectionData("test_path")
    with test_instance._connect_to_database() as cursor:
        assert cursor == mock_cursor

    mock_connect.assert_called_once_with(database=test_instance.database_path)
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()


def test_get_elections():
    """
    Test the retrieval of election names from the database.

    This test ensures that the get_elections method of the DatabaseElectionData
    class retrieves the correct list of election names from the database.
    """

    expected_elections = ["election1", "election2"]

    with patch.object(target=election_data.DatabaseElectionData,
                      attribute="_connect_to_database",
                      new=mock_connection):
        test_instance = election_data.DatabaseElectionData("")

        actual_elections = test_instance.get_elections()
        assert expected_elections == actual_elections


@pytest.mark.parametrize("election, expected_regions",
                         [("election1", ['Region1', 'Region2']),
                          ("election2", ['Region3', 'Region2'])])
def test_get_regions(election, expected_regions):
    """
    Test the retrieval of regions for a specific election from the database.

    This test ensures that the get_regions method of the DatabaseElectionData
    class retrieves the correct list of regions for a given election from the
    database.
    """

    with patch.object(target=election_data.DatabaseElectionData,
                      attribute="_connect_to_database",
                      new=mock_connection):
        test_instance = election_data.DatabaseElectionData("")
        actual_regions = test_instance.get_regions(election_name=election)
        assert expected_regions == actual_regions


def test_get_vote_data_no_params():
    """
    Test the retrieval of vote data for an election without specifying additional
    parameters.

    This test ensures that the get_vote_data method of the DatabaseElectionData
    class retrieves the correct parties and votes for a specified election without
    additional parameters.
    """

    expected_parties = ["PartyA", "PartyB"]
    expected_votes = np.array([[10, 20], [30, 40]], dtype=np.float64)

    with patch.object(target=election_data.DatabaseElectionData,
                      attribute="_connect_to_database", new=mock_connection):
        test_instance = election_data.DatabaseElectionData("")

        actual_parties, actual_votes = test_instance.get_vote_data(
            election_name="election1")

        assert expected_parties == actual_parties
        assert np.array_equal(expected_votes, actual_votes)


def test_get_vote_data_by_region_when_region_present():
    """
    Test the retrieval of vote data for an election and specific region when
    the region is present.

    This test ensures that the get_vote_data method of the DatabaseElectionData
    class retrieves the correct parties and votes for a specified election and
    region when the region is present in the database.
    """

    expected_parties = ["PartyA", "PartyB"]
    expected_votes = np.array([[10, 20]], dtype=np.float64)

    with patch.object(target=election_data.DatabaseElectionData,
                      attribute="_connect_to_database", new=mock_connection):
        test_instance = election_data.DatabaseElectionData("mocked_path")

        actual_parties, actual_votes = test_instance.get_vote_data(
            election_name="election1", region="Region1")

        assert expected_parties == actual_parties
        assert np.array_equal(expected_votes, actual_votes)


def test_get_vote_data_by_region_when_region_not_present():
    """
    Test the retrieval of vote data for an election and specific region when the
    region is not present.

    This test ensures that the get_vote_data method of the DatabaseElectionData
    class handles the case where the specified region is not present in the
    database, returning empty lists for parties and votes.
    """

    expected_parties = []
    expected_votes = np.array([], dtype=np.float64)

    with patch.object(target=election_data.DatabaseElectionData,
                      attribute="_connect_to_database", new=mock_connection):
        test_instance = election_data.DatabaseElectionData("mocked_path")

        actual_parties, actual_votes = test_instance.get_vote_data(
            election_name="election1", region="Does not exist")

        assert expected_parties == actual_parties
        assert np.array_equal(expected_votes, actual_votes)


def test_get_vote_data_ignore_other_when_other_present():
    """
    Test the retrieval of vote data for an election while ignoring 'other'
    parties when 'other' is present.

    This test ensures that the get_vote_data method of the DatabaseElectionData
    class retrieves the correct parties and votes for a specified election while
    excluding 'other' parties, when 'other' parties are present in the database.
    """

    expected_parties = ["PartyC"]
    expected_votes = np.array([[50], [70]], dtype=np.float64)

    with patch.object(target=election_data.DatabaseElectionData,
                      attribute="_connect_to_database", new=mock_connection):
        test_instance = election_data.DatabaseElectionData("mocked_path")

        actual_parties, actual_votes = test_instance.get_vote_data(
            election_name="election2", ignore_other=True)

        assert expected_parties == actual_parties
        assert np.array_equal(expected_votes, actual_votes)


def test_get_vote_data_ignore_other_when_other_not_present():
    """
    Test the retrieval of vote data for an election while ignoring 'other'
    parties when 'other' is not present.

    This test ensures that the get_vote_data method of the DatabaseElectionData
    class retrieves the correct parties and votes for a specified election while
    excluding 'other' parties, when 'other' parties are not present in the
    database.
    """

    expected_parties = ["PartyA", "PartyB"]
    expected_votes = np.array([[10, 20], [30, 40]], dtype=np.float64)

    with patch.object(target=election_data.DatabaseElectionData,
                      attribute="_connect_to_database", new=mock_connection):
        test_instance = election_data.DatabaseElectionData("mocked_path")

        actual_parties, actual_votes = test_instance.get_vote_data(
            election_name="election1", ignore_other=True)

        assert expected_parties == actual_parties
        assert np.array_equal(expected_votes, actual_votes)
