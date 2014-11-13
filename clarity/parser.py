import datetime
from collections import namedtuple

import dateutil.parser
from lxml import etree

class JurisdictionResults(object):
    """All results from a jurisdiction's detail XML result files"""
    def __init__(self):
        self.timestamp = None
        self.election_name = None
        self.election_date = None
        self.region = None
        self.total_voters = None
        self.ballots_cast = None
        self._precincts = []
        self._precinct_lookup = {}
        self._contests = []

    def parse(self, s):
        tree = etree.fromstring(s)
        self.timestamp = self._parse_timestamp(tree)
        self.election_name = self._parse_election_name(tree)
        self.election_date = self._parse_election_date(tree)
        self.region = self._parse_region(tree)
        self.total_voters = self._parse_total_voters(tree)
        self.ballots_cast = self._parse_ballots_cast(tree)
        self.voter_turnout = self._parse_voter_turnout(tree)

        self._precincts = self._parse_precincts(tree)
        self._precinct_lookup = {p.name: p for p in self._precincts}
        self._contests = self._parse_contests(tree)

    def _parse_timestamp(self, tree):
        return dateutil.parser.parse(tree.xpath('/ElectionResult/Timestamp')[0].text)

    def _parse_election_name(self, tree):
        return tree.xpath('/ElectionResult/ElectionName')[0].text

    def _parse_election_date(self, tree):
        dt = datetime.datetime.strptime(tree.xpath('/ElectionResult/ElectionDate')[0].text, '%m/%d/%Y')
        return datetime.date(dt.year, dt.month, dt.day)

    def _parse_region(self, tree):
        return tree.xpath('/ElectionResult/Region')[0].text

    def _parse_total_voters(self, tree):
        return int(tree.xpath('/ElectionResult/VoterTurnout')[0].values()[0])

    def _parse_ballots_cast(self, tree):
        return int(tree.xpath('/ElectionResult/VoterTurnout')[0].values()[1])

    def _parse_voter_turnout(self, tree):
        return float(tree.xpath('/ElectionResult/VoterTurnout')[0].values()[2])

    def _parse_precincts(self, tree):
        precincts = []
        precinct_els = tree.xpath('/ElectionResult/VoterTurnout/Precincts/Precinct')
        for el in precinct_els:
            precincts.append(Precinct(
              name=el.attrib['name'],
              total_voters=int(el.attrib['totalVoters']),
              ballots_cast=int(el.attrib['ballotsCast']),
              percent_reporting=float(el.attrib['percent_reporting'])
            ))
        return precincts

    @property
    def precincts(self):
        return self._precincts

    @property
    def contests(self):
        return self._contests

    @property
    def results(self):
        results = []
        for c in self.contests:
            results.extend(c.results)
        return results

    def _parse_contests(self, tree, precinct_lookup):
        contest_els = tree.xpath('/ElectionResult/Contest')
        return [self._parse_contest(el) for el in contest_els]

    def _parse_contest(self, el, precinct_lookup):
        contest = Contest(
           key=el.attrib['key'],
           text=el.attrib['text'],
           vote_for=int(el.attrib['voteFor']),
           is_question=self._parse_boolean(el.attrib['isQuestion']),
           precincts_reporting=int(el.attrib['precincts_reporting']),
           precincts_reported=int(el.attrib['precincts_reported'])
        )

        for r in self._parse_no_choice_results(el, precinct_lookup, contest):
            contest.add_result(r)

        for c in self._parse_choices(el, precinct_lookup, contest):
            contest.add_choice(c)
            
        return contest

    def _parse_no_choice_results(self, el, precinct_lookup, contest):
        results = []
        vote_type_els = el.xpath('/VoteType')
        for vt_el in vote_type_els:
            vote_type = vt_el.attrib['name']
            results.append(Result(
                contest=contest,
                vote_type=vote_type,
                votes=int(vt_el.attrib['votes'])
            ))
            for precinct_el in vt_el.xpath('/Precinct'):
                precinct = precinct_lookup[precinct_el.attrib['name']]
                results.append(Result(
                    vote_type=vote_type,
                    precinct=precinct,
                    votes=int(precinct_el.attrib['votes'])
                ))

        return results

    def _parse_choices(self, el, precinct_lookup):
        return [self._parse_choice(c_el, precinct_lookup)
                for c_el in el.xpath('Choice')]

    def _parse_choice(self, el, precinct_lookup, contest):
        choice = Choice(
            contest=contest,
            key=el.attrib['key'],
            text=el.attrib['text'],
            total_votes=el.attrib['totalVotes'],
        )
        vt_el = el.xpath('/VoteType')
        vote_type = vt_el.attrib['name']
        choice_results = []
        choice_results.append(Result(
          contest=contest,    
          vote_type=vote_type,
          votes=int(vt_el.attrib['votes']),
          choice=choice
        ))

        for precinct_el in vt_el.xpath('/Precinct'):
            precinct = precinct_lookup[precinct_el.attrib['name']]
            choice_results.append(Result(
                contest=contest,    
                vote_type=vote_type,
                precinct=precinct,
                votes=int(precinct_el.attrib['votes']),
                choice=choice
            ))

        return choice

    def _parse_boolean(self, s):
        return s == "true"
        
Precinct = namedtuple('Precinct', ['name', 'total_voters', 'ballots_cast', 'percent_reporting'])

class Contest(namedtuple('Contest', ['key', 'text', 'vote_for', 'is_question',
        'precincts_reporting', 'precincts_reported'])):
    def __init__(self, *args, **kwargs):
        super(Contest, self).__init__(*args, **kwargs)
        self._choices = []
        self._results = []

    @property
    def results(self):
        return self._results

    @property
    def choices(self):
        return self._choices

    def add_result(self, r):
        self._results.append(r)

    def add_choice(self, c):
        self._choices.append(c)
        self._results.extend(c.results)
        
class Choice(namedtuple('Choice', ['contest', 'key', 'text', 'total_votes'])):
    def __init__(self, *args, **kwargs):
        self._results = []

    @property
    def results(self):
        return self._results

    def add_result(self, r):
        self._results.append(r)


Result = namedtuple('Result', ['contest', 'vote_type', 'precinct', 'votes',
    'choice'])

