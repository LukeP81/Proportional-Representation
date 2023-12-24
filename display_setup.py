from typing import Tuple, Union, Dict

import streamlit as st

from database_retriever import get_table_names
from election_base import Election


def configure_page():
    st.set_page_config(page_title="Proportional Representation",
                       page_icon="🗳️",
                       layout="wide", )  # todo:menu


def improve_election_readability(
        election: str
) -> str:
    """
    Replace election year with more readable form.
    This only affects 1974 elections.

    :param election: Election year.
    :type election: str
    :return: Comprehensible election title.
    :rtype: str
    """

    replacement_names = {"1974F": "1974 February", "1974O": "1974 October"}
    return replacement_names.get(election, election)


def display_title(
        election_year: str
) -> None:
    """
    Display the election title at the center of the page.

    :param election_year: Selected election year.
    :type election_year: str
    """

    title = f"{improve_election_readability(election_year)} Election "
    title_html = f"""
        <p style='text-align: center;
                font-size: 48px;
                font-weight: bold;'>
            {title}
        </p>"""
    st.markdown(title_html, unsafe_allow_html=True)


def setup_sidebar_options(

) -> Dict[str, Union[str, bool, int]]:
    """
    Display and retrieve configuration options from the Streamlit sidebar.

    :return: Tuple of selected options.
    :rtype: Tuple[str, bool, bool, bool, int]
    """

    years = get_table_names()
    election_year = st.sidebar.select_slider(
        label="Election Year",
        options=years,
        value=years[-1],
        format_func=improve_election_readability,
        key="sidebar_election_year",
        help="Use the slider to select the election year"
    )

    pr_by_region_options = {"By Region": True, "Entire Electorate": False, }
    pr_by_region_radio = st.sidebar.radio(
        label="PR method",
        options=pr_by_region_options.keys(),
        key="sidebar_pr_pr_by_region",
        help="""Select how the PR will be performed by the D'Hondt method:
             \n-By Region: Utilizes individual regions for PR and sums the seats
             \n-Entire Electorate: Performs PR directly on the total votes"""
    )
    pr_by_region = pr_by_region_options[pr_by_region_radio]

    ignore_other_pr = st.sidebar.toggle(
        label="Ignore Other in PR", value=True,
        key="sidebar_ignore_other_pr",
        help="Exclude votes classified as 'Other' from the PR calculation"
    )

    tab_layout = st.sidebar.toggle(
        label="Tab format",
        value=False,
        key="sidebar_tab_format",
        help="Display the page in tab format if enabled"
    )

    maximum_coalition_size = st.sidebar.number_input(
        label="Maximum Coalition Size",
        min_value=2,
        value=3,
        key="sidebar_maximum_coalition_size",
        help="The maximum number of parties allowed in a coalition"
    )

    return {
        "election_year": election_year,
        "pr_by_region": pr_by_region,
        "ignore_other_pr": ignore_other_pr,
        "tab_layout": tab_layout,
        "maximum_coalition_size": maximum_coalition_size
    }


def display():
    configure_page()
    sidebar_options = setup_sidebar_options()
    display_title(sidebar_options["election_year"])
    return sidebar_options


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
        for key in set(system1_results) | set(system2_results)}
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

    differences = _compare_voting_systems_seat_difference(
        system1_election.results,
        system2_election.results)
    st.header("Seats Gained/Lost")
    left_column, right_column = st.columns(2)

    for i, (metric, value) in enumerate(differences.items()):
        if value == 0:
            continue
        if i % 2 == 0:
            left_column.metric(label=metric,
                               value=metric,
                               delta=value,
                               label_visibility="hidden")
        else:
            right_column.metric(label=metric,
                                value=metric,
                                delta=value,
                                label_visibility="hidden")
