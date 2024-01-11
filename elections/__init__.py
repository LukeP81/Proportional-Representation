"""
Package for elections

Imported Classes, Enumerations and Errors:
- Election: Abstract base class for representing elections.
- NotCalculatedError: Error for attempting to access yet to be calculated results.
- FirstPastThePost: Represents a First Past The Post election.
- ProportionalRepresentation: Represents a Proportional Representation election.
- MethodForPR: Enumeration for different methods of Proportional Representation.
"""

from elections.base_election import Election, NotCalculatedError
from elections.fptp import FirstPastThePost
from elections.pr import ProportionalRepresentation, MethodForPR
