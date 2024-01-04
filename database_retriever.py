"""
Database Retriever Module

This module provides functions for connecting to an SQLite database, retrieving
information about tables, and obtaining specific data for analysis.

The module includes the following functions:
- connect_to_database: Context manager for establishing a connection to the
  SQLite database.
- get_table_names: Retrieves the names of all tables in the connected database.
- get_regions: Retrieves distinct country/region names from a specified table.
- get_vote_data: Retrieves vote data from a specified table, optionally filtered
  by country/region and ignoring the 'Votes-Other' column.
"""

from contextlib import contextmanager
from typing import List, Optional, Tuple
import sqlite3

import numpy as np
import streamlit as st


@contextmanager
def connect_to_database():
    """
    Context manager to connect to the SQLite database.

    :yield: SQLite cursor
    :rtype: sqlite3.Cursor
    """

    conn = sqlite3.connect(database="elections.db")
    cursor = conn.cursor()
    try:
        yield cursor
    finally:
        cursor.close()
        conn.close()


@st.cache_data
def get_table_names() -> List[str]:
    """
    Retrieves the names of all tables present in the SQLite database.

    :return: List of table names
    :rtype: List[str]
    """

    with connect_to_database() as cursor:
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        table_names = cursor.fetchall()
    table_names = [name[0] for name in table_names]

    return table_names


@st.cache_data
def get_regions(table_name: str) -> List[str]:
    """
    Retrieves distinct country/region names from a specified table in the
    SQLite database.

    :param table_name: Name of the table
    :type table_name: str
    :return: List of distinct country/region names
    :rtype: List[str]
    """

    with connect_to_database() as cursor:
        cursor.execute(f"SELECT DISTINCT [Country/Region] FROM [{table_name}];")
        return [region[0] for region in cursor.fetchall()]


@st.cache_data
def get_vote_data(
        table_name: str,
        region: Optional[str] = None,
        ignore_other: bool = False
) -> Tuple[List[str], np.ndarray]:
    """
    Retrieves vote data from a specified table in the SQLite database.

    :param table_name: Name of the table
    :type table_name: str
    :param region: Name of the country/region. If None,
                   retrieves data for all regions.
    :type region: Optional[str]
    :param ignore_other: Whether to ignore the 'Votes-Other' column in the result.
    :type ignore_other: bool
    :return: Tuple containing a list of party names and a NumPy array of vote data
    :rtype: Tuple[List[str], np.ndarray]
    """

    with connect_to_database() as cursor:
        cursor.execute(f"PRAGMA table_info([{table_name}]);")
        columns = [f"[{column[1]}]" for column in cursor.fetchall() if
                   column[1].startswith('Votes-')]
        if ignore_other:
            columns.remove("[Votes-Other]")
        columns_str = ', '.join(columns)

        query = f"SELECT {columns_str} FROM [{table_name}];"
        if region is not None:
            query = query[:-1] + f" WHERE [Country/Region] = '{region}';"
        cursor.execute(query)
        result = cursor.fetchall()

        parties = [name[7:-1].strip() for name in columns]
        votes = np.array(result, dtype=np.float64)
        votes = np.nan_to_num(votes, nan=0)

    return parties, votes
