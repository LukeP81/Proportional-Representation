import streamlit as st

from display_setup import display_initial_page
from election_fptp import FPTP
from election_pr import PR
from ruling_government import display_governments_comparison
from seat_comparison import display_seat_comparison
from seat_plot import display_seat_plots

sidebar_options = display_initial_page()

fptp = FPTP(election_name=sidebar_options["election_year"],
            maximum_coalition_size=sidebar_options["maximum_coalition_size"])
fptp.calculate_results()
fptp.calculate_coalitions()

pr = PR(election_name=sidebar_options["election_year"],
        maximum_coalition_size=sidebar_options["maximum_coalition_size"],
        ignore_other=sidebar_options["ignore_other_pr"],
        pr_by_region=sidebar_options["pr_by_region"])
pr.calculate_results()
pr.calculate_coalitions()

if sidebar_options["tab_layout"]:
    seat_plot_tab, seats_comparison_tab, coalitions_tab = st.tabs(
        ["Seat Plot", "Seats Gained/Lost", "Ruling Party/Coalitions"])

    with seat_plot_tab:
        display_seat_plots(system1_election=fptp, system2_election=pr)

    with seats_comparison_tab:
        display_seat_comparison(system1_election=fptp, system2_election=pr)

    with coalitions_tab:
        display_governments_comparison(system1_election=fptp,
                                       system2_election=pr,
                                       maximum_coalition_size=sidebar_options[
                                           "maximum_coalition_size"])


else:
    display_seat_plots(system1_election=fptp, system2_election=pr)
    st.divider()
    display_seat_comparison(system1_election=fptp, system2_election=pr)
    st.divider()
    display_governments_comparison(system1_election=fptp,
                                   system2_election=pr,
                                   maximum_coalition_size=sidebar_options[
                                       "maximum_coalition_size"])
