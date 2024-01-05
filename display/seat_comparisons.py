"""
Seat Comparisons Display Module

This module provides functions for displaying a comparison of the number of
seats for two different voting systems.

The module includes the following functions:
- _compare_voting_systems_seat_difference: Compares the results of two voting
  systems and calculates the seat difference for each party.
- display_seat_comparison: Displays a comparison of the number of seats for
  two different voting systems using Streamlit metrics.
"""

import streamlit as st

from elections.election_base import Election


def _compare_voting_systems_seat_difference(
        system1_results: dict,
        system2_results: dict
) -> dict:
    """
    Compares the results of two different voting systems and calculates
    the difference in seats for each party.

    :param system1_results: The results of the first voting system.
    :type system1_results: dict
    :param system2_results: The results of the second voting system.
    :type system2_results: dict
    :return: A sorted OrderedDict containing the differences in seats for each
             party between the two voting systems.
    :rtype: dict
    """

    differences = {
        key: int(system2_results.get(key, 0) - system1_results.get(key, 0))
        for key in set(system1_results) | set(system2_results)
        if int(system2_results.get(key, 0) - system1_results.get(key, 0)) != 0
    }

    return dict(sorted(differences.items(),
                       key=lambda x: abs(x[1]),
                       reverse=True))


def display_seat_comparison(
        system1_election: Election,
        system2_election: Election
) -> None:
    """
    Displays a comparison of the number of seats any particular party receives
    for two different voting systems using Streamlit metrics.

    :param system1_election: The election from of the first voting system.
    :type system1_election: Election
    :param system2_election: The election from of the second voting system.
    :type system2_election: Election
    """

    seat_differences = _compare_voting_systems_seat_difference(
        system1_results=system1_election.results,
        system2_results=system2_election.results)
    st.header("Seats Gained/Lost")
    st.write((f"*If {system2_election.election_type} "
              "was used instead of "
              f"{system1_election.election_type}*"))

    left_column, right_column = st.columns(2)
    for i, (metric, value) in enumerate(seat_differences.items()):

        if i > len(seat_differences)/2:
            right_column.metric(label=metric,
                               value=metric,
                               delta=value,
                               label_visibility="hidden")
        else:
            left_column.metric(label=metric,
                                value=metric,
                                delta=value,
                                label_visibility="hidden")
