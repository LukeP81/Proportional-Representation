"""
Abstract base class representing election data.

This module defines the ElectionData abstract base class, which serves as a
base class for handling various aspects of election data.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Tuple

import numpy as np


class ElectionData(ABC):
    """
    Abstract base class representing election data.

    Methods:
    - get_elections: Gets the names of usable elections.
    - get_regions: Gets distinct countries/regions for a specific election.
    - get_vote_data: Gets vote data for a specific election.
    """

    @abstractmethod
    def get_elections(
            self
    ) -> List[str]:
        """
        Gets the names of usable elections.

        :return: List of table names
        :rtype: List[str]
        """

    @abstractmethod
    def get_regions(
            self,
            election_name: str
    ) -> List[str]:
        """
        Gets distinct countries/regions for a specific election.

        :param election_name: Name of the election
        :type election_name: str
        :return: List of distinct country/region names
        :rtype: List[str]
        """

    @abstractmethod
    def get_vote_data(
            self,
            election_name: str,
            region: Optional[str] = None,
            ignore_other: bool = False
    ) -> Tuple[List[str], np.ndarray]:
        """
        Gets vote data for a specific election.

        :param election_name: Name of the table
        :type election_name: str
        :param region: Name of the country/region. If None,
                       retrieves data for all regions.
        :type region: Optional[str]
        :param ignore_other: Whether to ignore the votes from "other" candidates.
        :type ignore_other: bool
        :return: Tuple containing party names and a NumPy array of vote data.
        :rtype: Tuple[List[str], np.ndarray]
        """