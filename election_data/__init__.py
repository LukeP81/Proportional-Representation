"""
Package for election data

Contains:
- ElectionData: Abstract base class representing election data.
- DatabaseElectionData: Class for election data from a SQLite databases.
"""

from election_data.election_data_base import ElectionData
from election_data.database import DatabaseElectionData
