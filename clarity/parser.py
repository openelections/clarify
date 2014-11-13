from collections import namedtuple

from lxml import etree

class ElectionResult(object):
    """All results from a jurisdiction's detail XML result files"""
    # TODO: Decide if this name sucks since it actually represents a bunch
    # of results.

    def __init__(self):
        self.timestamp = None
        self.election_name = None
        self.election_date = None
        self.region = None
        self.total_voters = None
        self.ballots_cast = None
        self._precincts = []
        self._precinct_lookup = {}

    def parse(self, s):
        tree = etree.fromstring(s)
        self.timestamp = self._parse_timestamp(tree)
        self.election_name = self._parse_election_name(tree)
        self.election_date = self._parse_election_date(tree)
        self.region = self._parse_region(tree)
        self.total_voters = self._parse_total_voters(tree)
        self._ballots_cast = self._parse_ballots_cast(tree)

        self._precincts = self._parse_precincts(tree)

    def _parse_timestamp(self, tree):
        pass

    def _parse_election_name(self, tree):
        pass

    def _parse_election_date(self, tree):
        pass

    def _parse_region(self, tree):
        pass

    def _parse_total_voters(self, tree):
        pass

    def _parse_ballots_cast(self, tree):
        pass

    def _parse_precincts(self, tree):
        precinct_els = tree.xpath('/ElectionResult/VoterTurnout/Precincts/Precinct')
        for el in precinct_els:
            # TODO: Implement this
            pass
        
    @property
    def precincts(self):
        return self._precincts

Precinct = namedtuple('Precinct', ['name', 'total_voters', 'percent_reporting'])

Contest = namedtuple('Contest', ['key', 'text', 'vote_for', 'is_question',
    'precincts_reporting', 'precincts_reported'])

Result = namedtuple('Result', ['contest', 'vote_type', 'precinct', 'votes',
    'choice'])

Choice = namedtuple('Choice', ['key', 'text'])
