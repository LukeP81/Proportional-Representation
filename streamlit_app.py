"""
Streamlit App Module

This script defines a Streamlit web application for visualizing and comparing
election results under different voting systems.

Modules:
- `display.ruling_governments`: Functions to display comparisons of ruling
    governments between different election systems.
- `display.seat_comparisons`: Functions to display comparisons of seats
    gained/lost between different election systems.
- `display.seat_plots`: Functions to display seat plots for different election
    systems.
- `display.startup`: Functions for displaying the initial page and obtaining user
    input.

Classes:
- `elections.election_fptp.FirstPastThePost`: Class for conducting
    First-Past-The-Post (FPTP) elections.
- `elections.election_pr.ProportionalRepresentation`: Class for conducting
    Proportional Representation (PR) elections.

Main Execution:
1. Initializes the Streamlit app with the required modules.
2. Obtains user selection for election and configuration parameters.
3. Conducts FPTP and PR elections based on parameters.
4. Displays election results and comparisons using Streamlit components.

Usage:
Run the script using the Streamlit command: `streamlit run streamlit_app.py`
"""

import streamlit as st

from display.ruling_governments import display_governments_comparison
from display.seat_comparisons import display_seat_comparison
from display.seat_plots import display_seat_plots
from display.startup import display_initial_page, PageLayout
from elections.election_fptp import FirstPastThePost
from elections.election_pr import ProportionalRepresentation

sidebar_options = display_initial_page()

fptp_election = FirstPastThePost(
    election_name=sidebar_options["election_name"],
    maximum_coalition_size=sidebar_options["maximum_coalition_size"]
)
fptp_election.calculate_results()
fptp_election.calculate_coalitions()

pr_election = ProportionalRepresentation(
    election_name=sidebar_options["election_name"],
    maximum_coalition_size=sidebar_options["maximum_coalition_size"],
    ignore_other=sidebar_options["ignore_other_pr"],
    pr_method=sidebar_options["pr_method"]
)
pr_election.calculate_results()
pr_election.calculate_coalitions()

kwargs = {"system1_election": fptp_election,
          "system2_election": pr_election}

display_order = {"Seat Plot": display_seat_plots,
                 "Seats Gained/Lost": display_seat_comparison,
                 "Ruling Party/Coalitions": display_governments_comparison}

if sidebar_options["page_layout"] == PageLayout.TAB_LAYOUT:
    tabs = st.tabs(display_order.keys())
    for tab, display_function in zip(tabs, display_order.values()):
        with tab:
            display_function(**kwargs)

if sidebar_options["page_layout"] == PageLayout.SCROLLING_LAYOUT:
    for i, display_function in enumerate(display_order.values()):
        if i > 0:
            st.divider()
        display_function(**kwargs)
