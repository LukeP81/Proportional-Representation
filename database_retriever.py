import sqlite3
from contextlib import contextmanager
import numpy as np
import streamlit as st


@contextmanager
def connect_to_database():
    conn = sqlite3.connect("elections.db")
    cursor = conn.cursor()
    try:
        yield cursor
    finally:
        cursor.close()
        conn.close()


@st.cache_data
def get_table_names():
    with connect_to_database() as cursor:
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        table_names = cursor.fetchall()
    table_names = [name[0] for name in table_names]

    return table_names


@st.cache_data
def get_regions(table_name):
    with connect_to_database() as cursor:
        cursor.execute(f"SELECT DISTINCT [Country/Region] FROM [{table_name}];")
        return [region[0] for region in cursor.fetchall()]


@st.cache_data
def get_vote_data(table_name, region=None, ignore_other=False):
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
