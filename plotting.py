import json

from plotly import graph_objects as go
import numpy as np
import streamlit as st


def create_coloured_dot(colour, party, votes):
    dot_list = f"""
    <div class="custom-list-item">
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
            display: inline-block;
        ">{party} ({votes})</span>
    </div>
    """

    return dot_list


def get_legend(results):
    with open("party_colours.json") as file:
        party_colours = json.load(file)

    markdown_string = ""
    for party, votes in results.items():
        if votes == 0:
            continue
        colour = party_colours.get(party, "#808080")
        dot_list = create_coloured_dot(colour, party, votes)
        markdown_string += dot_list
    return markdown_string


def calculate_rows(total_votes, row_length=50):
    return int(np.ceil(total_votes / row_length))


def generate_scatter(x, y, num_seats, start_row=0, row_length=50):
    num_rows = calculate_rows(num_seats, row_length)
    end_row = start_row + num_rows

    x_grid, y_grid = np.meshgrid(x, y[start_row:end_row])
    x_flat = x_grid.flatten()[:num_seats]
    y_flat = y_grid.flatten()[:num_seats]

    return x_flat, y_flat, end_row


def generate_traces(results, start_x=0, x_width=50):
    with open("party_colours.json") as file:
        party_colours = json.load(file)

    max_y = 2000 // x_width
    x = np.linspace(start_x + 1, start_x + x_width, x_width)
    y = np.linspace(-1, -max_y, max_y)

    start_row = 0

    traces = []
    for party, seats in results.items():
        if seats == 0:
            continue
        x_flat, y_flat, start_row = generate_scatter(x=x,
                                                     y=y,
                                                     num_seats=seats,
                                                     start_row=start_row)
        party_colour = party_colours.get(party, "#808080")
        traces.append(go.Scatter(x=x_flat,
                                 y=y_flat,
                                 mode='markers',
                                 marker={"size": 8, "color": party_colour},
                                 name=f"{party} ({seats})", ))

    return traces, start_row


@st.cache_data
def create_plotly_figure(election, election2):
    offset = 15
    x_width = 50
    trace1, max_y = generate_traces(election, x_width=x_width)
    trace2, max_y1 = generate_traces(election2, start_x=offset + x_width,
                                     x_width=x_width)
    maxy = max(max_y, max_y1)
    fig = go.Figure()
    for trace in trace1:
        fig.add_trace(trace)
    for trace in trace2:
        fig.add_trace(trace)
    fig.update_layout(
        showlegend=False,
        plot_bgcolor='rgba(0,0,0,0)',
        margin={'l': 0, 'r': 0, 't': 0, 'b': 0},
        height=maxy * 15,
        xaxis={
            'showgrid': False,
            'zeroline': False,
            'showticklabels': False,
            'range': [0.5, offset + x_width * 2 + 0.5],

        },
        yaxis={
            'showgrid': False,
            'zeroline': False,
            'showticklabels': False,
            'range': [-(maxy + 0.5), -0.5]
        }
    )
    return fig


def plot(election, election2):
    fig = create_plotly_figure(election.results, election2.results)

    l, r = st.columns([14, 11])
    with l:
        st.header("First Past The Post")
    with r:
        st.header("Proportional Representation")

    st.plotly_chart(fig, use_container_width=True, config={"staticPlot": True})

    l, r = st.columns([14, 11])
    with l:
        st.markdown(get_legend(election.results), unsafe_allow_html=True)
    with r:
        st.markdown(get_legend(election2.results),
                    unsafe_allow_html=True)
