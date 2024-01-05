"""
Display and Configuration Module

This module provides functions for setting up the Streamlit page, displaying
initial components, and handling user interactions with the sidebar.

The module includes the following functions:
- startup: Sets up initial configurations for the Streamlit page.
- improve_election_readability: Replaces election year with a more readable form.
- setup_sidebar_options: Displays and retrieves configuration options from the
  Streamlit sidebar.
- change_current_election: Alters the current election in the session state based
  on the provided offset.
- next_button: Displays a button to navigate to the next election if available.
- previous_button: Displays a button to navigate to the previous election if
  available.
- display_title: Displays the election title at the center of the page.
- display_initial_page: Displays the initial components of the Streamlit page.

Enumerations:
- PageLayout: Represents different page layout options.
- MethodForPR: Defines different methods for Proportional Representation.
"""

from enum import Enum
from typing import Dict, Union

import streamlit as st

from database_retriever import get_table_names
from elections.election_pr import MethodForPR


class PageLayout(Enum):
    """
    Enumeration representing different page layout options.
    """

    TAB_LAYOUT = "Tab Layout"
    SCROLLING_LAYOUT = "Scrolling Layout"


ConfigurationOptionTypes = Union[str, PageLayout, bool, MethodForPR, int]


def get_enum_value(enum_name: Enum) -> str:
    """
    Get the value associated with an enum member.

    :param enum_name: The enum member.
    :type enum_name: Enum
    :return: The value associated with the enum member.
    :rtype: str
    """

    return str(enum_name.value)


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


def startup() -> None:
    """
    Sets everything that must be set at the start of running.
    """

    st.set_page_config(
        page_title="Proportional Representation",
        page_icon="🗳️",
        layout="wide",
        menu_items={
            "Get help":
                "https://github.com/LukeP81/Proportional-Representation",
            "Report a Bug":
                "https://github.com/LukeP81/Proportional-Representation",
            "About": """
            This Streamlit app allows you to explore and compare election results
            under First-past-the-post and Proportional representation voting
            systems. You can visualize seat plots, compare seats gained/lost, and
            analyze ruling governments based on user-configurable parameters.
            - *Use the sidebar to select the election and set configuration
            parameters.*\n
            Author: Luke Peart, lukepeart81@gmail.com,
             [Github](https://github.com/LukeP81)
            """
        }
    )

    st.session_state["elections"] = get_table_names()
    if "elections" not in st.session_state:
        st.session_state["elections"] = get_table_names()
    if "current_election" not in st.session_state:
        st.session_state["current_election"] = st.session_state["elections"][-1]


def setup_sidebar_options() -> Dict[str, ConfigurationOptionTypes]:
    """
    Display and retrieve configuration options from the Streamlit sidebar.

    :return: Dict of selected options.
    :rtype: Dict[str, Union[str, PageLayout, bool, MethodForPR, int]]
    """

    def on_election_change():
        chosen_election = st.session_state["sidebar_election_name"]
        st.session_state["current_election"] = chosen_election

    election_options = list(reversed(st.session_state["elections"]))
    election_name = st.sidebar.selectbox(
        label="Election",
        options=election_options,
        index=election_options.index(st.session_state["current_election"]),
        format_func=improve_election_readability,
        key="sidebar_election_name",
        help="Use the slider to select the election",
        on_change=on_election_change
    )

    pr_method = st.sidebar.radio(
        label="PR Method",
        options=MethodForPR,
        format_func=get_enum_value,
        key="sidebar_pr_by_region",
        help="""Select how the PR will be performed by the D'Hondt method:
             \n-By Region: Utilizes individual regions for PR and sums the seats
             \n-Entire Electorate: Performs PR directly on the total votes"""
    )

    ignore_other_pr = st.sidebar.toggle(
        label="Ignore Other in PR", value=True,
        key="sidebar_pr_ignore_other",
        help="Exclude votes classified as 'Other' from the PR calculation"
    )
    maximum_coalition_size = st.sidebar.number_input(
        label="Maximum Coalition Size",
        min_value=2,
        value=3,
        key="sidebar_maximum_coalition_size",
        help="The maximum number of parties allowed in a coalition"
    )
    page_layout = st.sidebar.radio(
        label="Page Layout",
        options=PageLayout,
        format_func=get_enum_value,
        key="sidebar_page_layout",
        help="""Select how the page is displayed:
             \n-Tab Layout: the different sections are accessed through tabs
             \n-Scrolling Layout: the different sections are accessed through 
                scrolling"""
    )

    return {
        "election_name": election_name,
        "pr_method": pr_method,
        "ignore_other_pr": ignore_other_pr,
        "page_layout": page_layout,
        "maximum_coalition_size": maximum_coalition_size
    }


def change_current_election(election_offset: int = 0) -> None:
    """
    Alters the current election in the session state based on the provided
    election offset.

    :param election_offset: An integer representing the change in index to
        navigate to different elections. Default is 0 (no alteration).
    :type election_offset: int
    """

    elections = st.session_state["elections"]
    current_election = st.session_state["current_election"]
    next_election = elections[elections.index(current_election) + election_offset]
    st.session_state["current_election"] = next_election


def next_button():
    """
    Displays a button to navigate to the previous election if available.
    """

    if st.session_state["current_election"] != st.session_state["elections"][-1]:
        st.button(label="Next Election",
                  key="button_next_election",
                  on_click=change_current_election,
                  args=(+1,))


def previous_button() -> None:
    """
    Displays a button to navigate to the previous election if available.
    """

    if st.session_state["current_election"] != st.session_state["elections"][0]:
        st.button(label="Previous Election",
                  key="button_previous_election",
                  on_click=change_current_election,
                  args=(-1,))


def display_title(
        election_name: str
) -> None:
    """
    Display the election title at the center of the page.

    :param election_name: Selected election year.
    :type election_name: str
    """

    title = f"{improve_election_readability(election_name)} Election "
    title_html = f"""
        <p style='text-align: center;
                font-size: 48px;
                font-weight: bold;'>
            {title}
        </p>"""
    st.markdown(title_html, unsafe_allow_html=True)


def display_initial_page() -> Dict[str, ConfigurationOptionTypes]:
    """
    Display the initial components of the Streamlit page.

    :return: Dictionary containing selected option from the sidebar.
    :rtype: Dict[str, Union[str, bool, int]]
    """

    startup()
    sidebar_options = setup_sidebar_options()

    _, centre, _ = st.columns([1, 1, 1])
    with centre:
        with st.container():
            left_column, right_column = centre.columns(2)
            with left_column:
                previous_button()
            with right_column:
                next_button()

    display_title(election_name=sidebar_options["election_name"])

    return sidebar_options
