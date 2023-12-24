import streamlit as st

from election_fptp import FPTP
from plotting import plot
from election_pr import PR
from display_setup import display, display_seat_comparison

sidebar_options = display()

fptp = FPTP(year=sidebar_options["election_year"],
            maximum_coalition_size=sidebar_options["maximum_coalition_size"])
fptp.calculate_results()
fptp.find_valid_coalitions()

pr = PR(year=sidebar_options["election_year"],
        maximum_coalition_size=sidebar_options["maximum_coalition_size"],
        ignore_other=sidebar_options["ignore_other_pr"],
        pr_by_region=sidebar_options["pr_by_region"])
pr.calculate_results()
pr.find_valid_coalitions()

if sidebar_options["tab_layout"]:
    f, m = st.tabs(["Figure", "metrics"])
    with f:
        plot(fptp, pr)
    # with m:
    #     display_metrics(results_fptp, pr_results=results_pr)

else:
    plot(fptp, pr)
    st.divider()
    display_seat_comparison(fptp, pr)
    st.divider()
