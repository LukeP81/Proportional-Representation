from typing import Dict, Union

import streamlit as st

from database_retriever import get_table_names


def configure_page() -> None:
    """
    Configures the Streamlit page options.
    """

    st.set_page_config(
        page_title="Proportional Representation",
        page_icon="🗳️",
        layout="wide",  # todo: Implement additional configuration for the menu
    )


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


def setup_sidebar_options() -> Dict[str, Union[str, bool, int]]:
    """
    Display and retrieve configuration options from the Streamlit sidebar.

    :return: Dict of selected options.
    :rtype: Dict[str, Union[str, bool, int]]
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
        key="sidebar_pr_by_region",
        help="""Select how the PR will be performed by the D'Hondt method:
             \n-By Region: Utilizes individual regions for PR and sums the seats
             \n-Entire Electorate: Performs PR directly on the total votes"""
    )
    pr_by_region = pr_by_region_options[pr_by_region_radio]

    ignore_other_pr = st.sidebar.toggle(
        label="Ignore Other in PR", value=True,
        key="sidebar_pr_ignore_other",
        help="Exclude votes classified as 'Other' from the PR calculation"
    )

    tab_layout = st.sidebar.toggle(
        label="Tab layout",
        value=False,
        key="sidebar_tab_layout",
        help="Displays the page in a tab layout if enabled"
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


def display_initial_page() -> Dict[str, Union[str, bool, int]]:
    """
    Display the initial components of the Streamlit page.

    :return: Dictionary containing selected option from the sidebar.
    :rtype: Dict[str, Union[str, bool, int]]
    """

    configure_page()
    sidebar_options = setup_sidebar_options()
    display_title(election_year=sidebar_options["election_year"])
    return sidebar_options
