"""
Database Election Data Retrieval Module

This module provides a class, DatabaseElectionData, for retrieving election
data from SQLite databases.
"""

from contextlib import contextmanager
from typing import List, Optional, Tuple
import sqlite3

import numpy as np

from election_data.election_data_base import ElectionData


class DatabaseElectionData(ElectionData):
    """
    Election data retrieval class for SQLite databases.

    Attributes:
    - database_path (str): The path to the SQLite database file.

    Methods:
    - connect_to_database: Context manager for connecting to the SQLite database.
    - execute_query: Executes an SQL query and returns the result.
    - get_elections: Gets the names of usable elections.
    - get_regions: Gets distinct country/region names for a specific election.
    - get_vote_data: Gets vote data for a specific election.
    """

    def __init__(
            self,
            database_path: str
    ):
        """
        :param database_path: Path to the SQLite database file.
        :type database_path: str
        """

        self.database_path = database_path

    @contextmanager
    def _connect_to_database(self):
        """
        Context manager to connect to the SQLite database.

        :yield: SQLite cursor
        :rtype: sqlite3.Cursor
        """

        conn = sqlite3.connect(database=self.database_path)
        cursor = conn.cursor()
        try:
            yield cursor
        finally:
            cursor.close()
            conn.close()

    def _execute_query(
            self,
            query: str
    ) -> list:
        """
        Executes an SQL query and returns the result.

        :param query: SQL query string
        :type query: str
        :return: Result of the SQL query
        :rtype: list
        """

        with self._connect_to_database() as cursor:
            cursor.execute(query)
            return cursor.fetchall()

    def get_elections(
            self
    ) -> List[str]:

        query = "SELECT name FROM sqlite_master WHERE type=\"table\";"
        return [name[0] for name in self._execute_query(query=query)]

    def get_regions(
            self,
            election_name: str
    ) -> List[str]:

        query = f"SELECT DISTINCT [Country/Region] FROM [{election_name}];"
        return [region[0] for region in self._execute_query(query)]

    def get_vote_data(
            self,
            election_name: str,
            region: Optional[str] = None,
            ignore_other: bool = False
    ) -> Tuple[List[str], np.ndarray]:

        party_columns = self._get_party_columns(election_name, ignore_other)
        joined_columns = ", ".join(party_columns)
        query = f"SELECT {joined_columns} FROM \"{election_name}\";"
        if region is not None:
            query = f"{query[:-1]} WHERE \"Country/Region\" = \"{region}\";"

        result = self._execute_query(query)
        if not result:
            party_columns = []

        party_names = [name[7:-1].strip() for name in party_columns]
        votes = np.array(result, dtype=np.float64)
        votes = np.nan_to_num(votes, nan=0)

        return party_names, votes

    def _get_party_columns(
            self,
            election_name: str,
            ignore_other: bool
    ) -> List[str]:
        """
        Retrieve the party columns for a specific election.

        :param election_name: The name of the election.
        :type election_name: str
        :param ignore_other: Whether to ignore the votes from "other" party.
        :type ignore_other: bool
        :return: A list of column names representing parties.
        :rtype: List[str]
        """

        columns_query = f"PRAGMA table_info(\"{election_name}\");"
        party_columns = [f"\"{column[1]}\""
                         for column in self._execute_query(columns_query)
                         if column[1].startswith("Votes-")]
        if ignore_other and "\"Votes-Other\"" in party_columns:
            party_columns.remove("\"Votes-Other\"")
        return party_columns
