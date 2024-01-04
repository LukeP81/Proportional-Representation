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
from display.startup import display_initial_page
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
    pr_by_region=sidebar_options["pr_by_region"]
)
pr_election.calculate_results()
pr_election.calculate_coalitions()

if sidebar_options["tab_layout"]:
    seat_plot_tab, seats_comparison_tab, coalitions_tab = st.tabs(
        ["Seat Plot", "Seats Gained/Lost", "Ruling Party/Coalitions"])

    with seat_plot_tab:
        display_seat_plots(
            system1_election=fptp_election,
            system2_election=pr_election)

    with seats_comparison_tab:
        display_seat_comparison(
            system1_election=fptp_election,
            system2_election=pr_election)

    with coalitions_tab:
        display_governments_comparison(
            system1_election=fptp_election,
            system2_election=pr_election,
            maximum_coalition_size=sidebar_options["maximum_coalition_size"])


else:
    display_seat_plots(
        system1_election=fptp_election,
        system2_election=pr_election)
    st.divider()
    display_seat_comparison(
        system1_election=fptp_election,
        system2_election=pr_election)
    st.divider()
    display_governments_comparison(
        system1_election=fptp_election,
        system2_election=pr_election,
        maximum_coalition_size=sidebar_options["maximum_coalition_size"])
