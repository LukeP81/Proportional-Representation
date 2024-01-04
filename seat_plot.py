import json
from typing import List, Tuple

from plotly import graph_objects as go
import numpy as np
import streamlit as st

from election_base import Election


def party_dot(
        party: str,
        votes: int,
        colour: str = "#808080"
) -> str:
    """
    Generate an HTML representation of a party dot, name and seats.

    :param party: The name of the political party.
    :type party: str
    :param votes: The number of seats achieved by the party.
    :type votes: int
    :param colour: The color of the dot.
    :type colour: str
    :return: An HTML string representing the party dot.
    :rtype: str
    """

    return f"""
    <div>
        <span style="
            font-size: 24px;
            border-radius: 50%;
            display: inline-block;
            margin-right: 5px;
            height: 20px;
            width: 20px;
            background-color: {colour};
            vertical-align: middle;">
        </span>
        <span style="
            font-size: 16px;
            vertical-align: middle;
            display: inline-block;">
            {party} ({votes})
        </span>
    </div>
    """


def party_legend(
        results: dict,
        party_colours: dict
) -> str:
    """
    Generate an HTML legend based on election results and party colors.

    :param results: A dictionary containing party names and their seats.
    :type results: dict
    :param party_colours: A dictionary containing party names and their colors.
    :type party_colours: dict
    :return: An HTML string representing the party legend.
    :rtype: str
    """

    party_dots = []
    for party, votes in results.items():
        if votes == 0:
            continue
        colour = party_colours.get(party, "#808080")
        party_dots.append(party_dot(party=party,
                                    votes=votes,
                                    colour=colour))
    return "".join(party_dots)


def seat_scatter_array(
        x_axis: np.ndarray,
        y_axis: np.ndarray,
        num_seats: int,
        start_row: int = 0,
        row_length: int = 50
) -> Tuple[np.ndarray, np.ndarray, int]:
    """
    Generate arrays for scatter plot coordinates based on the number of seats.

    :param x_axis: 1-dimensional array representing the x-axis values.
    :type x_axis: np.ndarray
    :param y_axis: 1-dimensional array representing the y-axis values.
    :type y_axis: np.ndarray
    :param num_seats: The number of seats to be plotted.
    :type num_seats: int
    :param start_row: The starting row for scatter plot generation.
    :type start_row: int
    :param row_length: The maximum number of seats per row.
    :type row_length: int
    :return: Tuple containing arrays for x and y coordinates, and the ending row.
    :rtype: Tuple[np.ndarray, np.ndarray, int]
    """

    num_rows = int(np.ceil(num_seats / row_length))
    end_row = start_row + num_rows

    x_grid, y_grid = np.meshgrid(x_axis, y_axis[start_row:end_row])
    flat_indices = np.arange(start=0, stop=num_seats)
    x_flat = x_grid.flatten()[flat_indices]
    y_flat = y_grid.flatten()[flat_indices]

    return x_flat, y_flat, end_row


def party_traces(
        results: dict,
        start_x: int = 0,
        row_length: int = 50
) -> Tuple[List[go.Scatter], int]:
    """
    Generate scatter plot traces for each party based on election results.

    :param results: A dictionary containing party names and their seats.
    :type results: dict
    :param start_x: The starting position on the x-axis for the first election.
    :type start_x: int
    :param row_length: The maximum number of seats per row.
    :type row_length: int
    :return: Tuple containing a list of Scatter traces and the ending row.
    :rtype: Tuple[List[go.Scatter], int]
    """

    with open(file="party_colours.json") as file:
        party_colours = json.load(fp=file)
    max_y = sum(results.values()) // row_length * 2
    x_axis = np.arange(start=start_x + 1, stop=start_x + row_length + 1)
    y_axis = np.arange(start=-1, stop=-(max_y + 1), step=-1)

    start_row = 0
    traces = []
    for party, seats in results.items():
        if seats == 0:
            continue
        x_flat, y_flat, start_row = seat_scatter_array(x_axis=x_axis,
                                                       y_axis=y_axis,
                                                       num_seats=seats,
                                                       start_row=start_row,
                                                       row_length=row_length)
        party_colour = party_colours.get(party, "#808080")
        traces.append(go.Scatter(x=x_flat,
                                 y=y_flat,
                                 mode='markers',
                                 marker={"size": 8, "color": party_colour},
                                 name=f"{party} ({seats})", ))

    return traces, start_row


def seat_plot_figure(
        election1_results: dict,
        election2_results: dict
) -> go.Figure:
    """
    Generate a Plotly figure for comparing two election results.

    :param election1_results: A dictionary containing party names and
           their corresponding votes for the first election.
    :type election1_results: dict
    :param election2_results: A dictionary containing party names and
           their corresponding votes for the second election.
    :type election2_results: dict
    :return: A Plotly Figure object.
    :rtype: go.Figure
    """

    offset = 15
    x_width = 50
    election1_traces, max_height1 = party_traces(results=election1_results,
                                                 row_length=x_width)
    election2_traces, max_height2 = party_traces(results=election2_results,
                                                 start_x=offset + x_width,
                                                 row_length=x_width)
    max_height = max(max_height1, max_height2)

    seat_plot = go.Figure()
    for trace in election1_traces:
        seat_plot.add_trace(trace=trace)
    for trace in election2_traces:
        seat_plot.add_trace(trace=trace)
    seat_plot.update_layout(height=max_height * 15,
                            margin={'l': 0, 'r': 0, 't': 0, 'b': 0},
                            plot_bgcolor='rgba(0,0,0,0)',
                            showlegend=False,
                            xaxis={
                                'showgrid': False,
                                'zeroline': False,
                                'showticklabels': False,
                                'range': [0.5, offset + x_width * 2 + 0.5], },
                            yaxis={
                                'showgrid': False,
                                'zeroline': False,
                                'showticklabels': False,
                                'range': [-(max_height + 0.5), -0.5], })
    return seat_plot


def display_seat_plots(
        system1_election: Election,
        system2_election: Election
) -> None:
    """
    Display side-by-side seat plots for two election systems.

    :param system1_election: An Election object for the first election system.
    :type system1_election: Election
    :param system2_election: An Election object for the second election system.
    :type system2_election: Election
    """

    seat_plot = seat_plot_figure(election1_results=system1_election.results,
                                 election2_results=system2_election.results)

    l, r = st.columns([14, 11])
    with l:
        st.header(system1_election.election_type)
    with r:
        st.header(system2_election.election_type)

    st.plotly_chart(figure_or_data=seat_plot,
                    use_container_width=True,
                    config={"staticPlot": True})

    with open(file="party_colours.json") as file:
        party_colours = json.load(fp=file)
    l, r = st.columns([14, 11])
    with l:
        st.markdown(party_legend(results=system1_election.results,
                                 party_colours=party_colours),
                    unsafe_allow_html=True)
    with r:
        st.markdown(party_legend(results=system2_election.results,
                                 party_colours=party_colours),
                    unsafe_allow_html=True)
