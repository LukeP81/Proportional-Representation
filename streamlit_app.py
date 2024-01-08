"""
Streamlit App Module

This script defines a Streamlit web application for visualizing and comparing
election results under different voting systems.

Main Execution:
1. Initializes the Streamlit app with the required modules.
2. Obtains user selection for election and configuration parameters.
3. Conducts FPTP and PR elections based on selection.
4. Displays election results and comparisons using Streamlit components.

Usage:
Run the script using the Streamlit command: `streamlit run streamlit_app.py`
"""

import display
import elections
import election_data

DATABASE_NAME = "elections.db"

vote_data = election_data.DatabaseElectionData(DATABASE_NAME)

chosen_election, sidebar_options = display.initial_page(
    election_options=vote_data.get_elections())

fptp_election = elections.fptp.FirstPastThePost(
    election_name=chosen_election,
    vote_data=vote_data,
    maximum_coalition_size=sidebar_options.maximum_coalition_size,
)
fptp_election.calculate_all()

pr_election = elections.pr.ProportionalRepresentation(
    election_name=chosen_election,
    vote_data=vote_data,
    maximum_coalition_size=sidebar_options.maximum_coalition_size,
    ignore_other=sidebar_options.ignore_other_pr,
    pr_method=sidebar_options.pr_method
)
pr_election.calculate_all()

comparisons = display.Comparisons(
    system1_election=fptp_election,
    system2_election=pr_election,
    display_methods=[display.seat_plots,
                     display.seat_comparison,
                     display.governments_comparison],
    tab_names=["Seat Plot",
               "Seats Gained/Lost",
               "Ruling Party/Coalitions"],
    layout=sidebar_options.page_layout
)
comparisons.display()
