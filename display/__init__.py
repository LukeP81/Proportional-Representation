"""
Package for display functionality

Contains:
- Comparisons: Class to facilitate the display of election comparisons.
- governments_comparison: Displays information about the ruling government under
  a specific election and compares ruling parties or coalitions between two
  electoral systems.
- seat_comparison: Displays a comparison of the number of seats for two different
  voting systems.
- seat_plots: Provides functions for displaying side-by-side seat plots for two
  election systems.
- initial_page: Sets up the Streamlit page, displays initial components, and
  handles user interactions with the sidebar.
- PageLayout: Enumeration representing different page layout options.
"""

from display.comparisons import Comparisons
from display.ruling_governments import governments_comparison
from display.seat_differences import seat_comparison
from display.seat_plots import seat_plots
from display.startup import initial_page, PageLayout
