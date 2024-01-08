"""
Comparisons Module

This module defines the Comparisons class, which facilitates the display of
election comparisons.
"""

from typing import List

import elections
from display.parameter_requirements import NotDecoratedError
from display.startup import PageLayout
import streamlit as st


class Comparisons:
    """
    Class representing a tool for displaying election comparisons.

    Attributes:
    - kwargs (dict): Dictionary containing election objects for the two systems.
    - display_methods (List[callable]): Functions for displaying comparisons.
    - tab_names (List[str]): List of names for tabs in the layout.
    - layout (PageLayout): Enumeration indicating the desired layout type.

    Methods:
    - display: Display the comparisons based on the specified layout.
    - _tab_layout: Display comparisons using a tab layout.
    - _scrolling_layout: Display comparisons using a scrolling layout.
    """

    def __init__(self,
                 system1_election: elections.Election,
                 system2_election: elections.Election,
                 display_methods: List[callable],
                 tab_names: List[str],
                 layout: PageLayout = PageLayout.TAB_LAYOUT,
                 ):
        """
        :param system1_election: The election object for the first system.
        :type system1_election: elections.Election
        :param system2_election: The election object for the second system.
        :type system2_election: elections.Election
        :param display_methods: List of decorated functions for displaying comparisons.
        :type display_methods: List[callable]
        :param tab_names: List of names for tabs in the layout.
        :type tab_names: List[str]
        :param layout: PageLayout enumeration indicating the desired layout type (default is TAB_LAYOUT).
        :type layout: PageLayout
        """

        for display_method in display_methods:
            if not (getattr(display_method, 'comparison_method', False)):
                raise NotDecoratedError(
                    f"Function {display_method.__name__} "
                    f"must be decorated with @comparison_method")

        if len(tab_names) != len(display_methods):
            raise ValueError(
                "Length of tab_names must match the number of display_methods.")

        self.kwargs = {"system1_election": system1_election,
                       "system2_election": system2_election}
        self.display_methods = display_methods
        self.tab_names = tab_names
        self.layout = layout

    def display(self) -> None:
        """
        Display the comparisons based on the specified layout.
        """

        if self.layout == PageLayout.TAB_LAYOUT:
            self._tab_layout()
        if self.layout == PageLayout.SCROLLING_LAYOUT:
            self._tab_layout()

    def _tab_layout(self) -> None:
        """
        Display comparisons using a tab layout.
        """

        tabs = st.tabs(self.tab_names)
        for tab, display_function in zip(tabs, self.display_methods):
            with tab:
                display_function(**self.kwargs)

    def _scrolling_layout(self) -> None:
        """
        Display comparisons using a scrolling layout.
        """

        for i, display_function in enumerate(self.display_methods):
            if i > 0:
                st.divider()
            display_function(**self.kwargs)
