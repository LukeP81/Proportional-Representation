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

from dataclasses import dataclass
from enum import Enum
from typing import List, Tuple

import streamlit as st

import elections


class PageLayout(Enum):
    """
    Enumeration representing different page layout options.
    """

    TAB_LAYOUT = "Tab Layout"
    SCROLLING_LAYOUT = "Scrolling Layout"


@dataclass
class ConfigurationOptions:
    """
    Data class representing configuration options for the election system.

    :param pr_method: The method used for Proportional Representation (PR).
    :type pr_method: elections.MethodForPR
    :param ignore_other_pr: Flag indicating whether to ignore other PR options.
    :type ignore_other_pr: bool
    :param page_layout: The layout configuration for pages.
    :type page_layout: page_layout.PageLayout
    :param maximum_coalition_size: The maximum size allowed for political
           coalitions.
    :type maximum_coalition_size: int
    """

    pr_method: elections.MethodForPR
    ignore_other_pr: bool
    page_layout: PageLayout
    maximum_coalition_size: int


def _get_enum_value(enum_name: Enum) -> str:
    """
    Get the value associated with an enum member.

    :param enum_name: The enum member.
    :type enum_name: Enum
    :return: The value associated with the enum member.
    :rtype: str
    """

    return str(enum_name.value)


def _improve_election_readability(
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


def _startup() -> None:
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
            "Report a bug":
                "https://github.com/LukeP81/Proportional-Representation",
            "About": """
            This Streamlit app allows you to explore and compare election results
            under First-past-the-post and Proportional Representation voting
            systems. You can visualize seat plots, compare seats gained/lost, and
            analyze ruling governments based on user-configurable parameters.
            - *Use the sidebar to set configuration parameters.*\n
            Author: Luke Peart, lukepeart81@gmail.com,
             [Github](https://github.com/LukeP81)
            """
        }
    )


def set_election(
        election_options: List[str]
) -> str:
    """
    Set the election using a Streamlit select box.

    :param election_options: A list of election options to be displayed in the
                             select box.
    :type election_options: List[str]

    :return: The selected election.
    :rtype: str
    """

    selected_election = st.selectbox(
        label="Election",
        options=list(reversed(election_options)),
        format_func=_improve_election_readability,
        key="sidebar_election_name",
        help="Use the slider to select the election",
    )
    return selected_election if selected_election is not None else \
        election_options[-1]


def _setup_sidebar_options() -> ConfigurationOptions:
    """
    Display and retrieve configuration options from the Streamlit sidebar.

    :return: Selected options.
    :rtype: ConfigurationOptions
    """

    pr_method = st.sidebar.radio(
        label="PR Method",
        options=elections.MethodForPR,
        format_func=_get_enum_value,
        key="sidebar_pr_by_region",
        help="""Select how the PR will be performed by the D'Hondt method:
             \n-By Region: Utilizes individual regions for PR and sums the seats
             \n-Entire Electorate: Performs PR directly on the total votes"""
    )
    if pr_method is None:
        pr_method = elections.MethodForPR.BY_REGION

    ignore_other_pr = st.sidebar.toggle(
        label="Ignore Other in PR", value=True,
        key="sidebar_pr_ignore_other",
        help="Exclude votes classified as 'Other' from the PR calculation"
    )

    maximum_coalition_size = int(st.sidebar.number_input(
        label="Maximum Coalition Size",
        min_value=2,
        value=3,
        key="sidebar_maximum_coalition_size",
        help="The maximum number of parties allowed in a coalition"
    ))

    page_layout = st.sidebar.radio(
        label="Page Layout",
        options=PageLayout,
        format_func=_get_enum_value,
        key="sidebar_page_layout",
        help="""Select how the page is displayed:
             \n-Tab Layout: the different sections are accessed through tabs
             \n-Scrolling Layout: the different sections are accessed through
                 scrolling"""
    )
    if page_layout is None:
        page_layout = PageLayout.TAB_LAYOUT

    return ConfigurationOptions(
        pr_method=pr_method,
        ignore_other_pr=ignore_other_pr,
        page_layout=page_layout,
        maximum_coalition_size=maximum_coalition_size
    )


def _title(
        election_name: str
) -> None:
    """
    Display the election title at the center of the page.

    :param election_name: Selected election year.
    :type election_name: str
    """

    title = f"{_improve_election_readability(election_name)} Election "
    title_html = f"""
        <p style='text-align: center;
                font-size: 48px;
                font-weight: bold;'>
            {title}
        </p>"""
    st.markdown(title_html, unsafe_allow_html=True)


def initial_page(
        election_options: List[str]
) -> Tuple[str, ConfigurationOptions]:
    """
    Display the initial components of the Streamlit page.

    :return: the chosen election and configuration options.
    :rtype: Tuple[str, ConfigurationOptions]
    """

    _startup()
    current = set_election(election_options)
    sidebar_options = _setup_sidebar_options()

    _title(election_name=current)

    return current, sidebar_options
