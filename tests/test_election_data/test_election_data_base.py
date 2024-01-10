"""
Tests for election_data.election_data_base.py
"""

import pytest

import election_data


@pytest.mark.parametrize(
    "method",
    ["get_elections", "get_regions", "get_vote_data"])
def test_get_elections(method):
    """
    Test the presence of specified methods in ElectionData abstract base class.
    """

    assert hasattr(election_data.ElectionData, method)