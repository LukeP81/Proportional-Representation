import streamlit as st

from election_base import Election


def display_ruling_government(election: Election) -> None:
    """
    Display information about the ruling government under a specific election.

    :param election: The Election object representing the election data.
    :type election: Election
    """

    st.subheader(f"Under {election.election_type}")
    coalitions = election.coalitions
    if len(coalitions) == 1:
        st.write(f"**Outright Winner**\n- {coalitions[0][0]}")
        return

    st.write("**Viable Coalitions**")
    if coalitions is None:
        st.error("No viable coalitions found.")
    for coalition_idx, coalition in enumerate(coalitions, start=1):
        party_list_items = "\n".join([f"- {party}" for party in coalition])
        bullet_points = f"*Coalition {coalition_idx}*\n{party_list_items}"
        st.markdown(bullet_points)


def display_governments_comparison(
        system1_election: Election,
        system2_election: Election,
        maximum_coalition_size: int
) -> None:
    """
    Display a comparison of viable ruling parties or coalitions between
    two electoral systems.

    :param system1_election: The Election object for the first electoral system.
    :type system1_election: Election
    :param system2_election: The Election object for the second electoral system.
    :type system2_election: Election
    :param maximum_coalition_size: The maximum allowed size for a coalition.
    :type maximum_coalition_size: int
    """

    st.header("Viable Ruling Party/Coalitions")
    st.write(
        f"*Only based on numbers of seats and a maximum coalition size of "
        f"{maximum_coalition_size} (configurable in sidebar)*")
    left_col, right_col = st.columns(2)

    with left_col:
        display_ruling_government(election=system1_election)

    with right_col:
        display_ruling_government(election=system2_election)
