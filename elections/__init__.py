"""
Package for elections

Imported Classes and Enumerations:
- Election: Abstract base class for representing elections.
- FirstPastThePost: Represents a First Past The Post election.
- ProportionalRepresentation: Represents a Proportional Representation election.
- MethodForPR: Enumeration for different methods of Proportional Representation.
"""

from elections.base import Election
from elections.fptp import FirstPastThePost
from elections.pr import ProportionalRepresentation, MethodForPR
