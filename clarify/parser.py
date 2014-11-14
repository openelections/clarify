import datetime
from collections import namedtuple

import dateutil.parser
from lxml import etree

class Parser(object):
    """All results from a jurisdiction's detail XML result files"""
    def __init__(self):
        self.timestamp = None
        self.election_name = None
        self.election_date = None
        self.region = None
        self.total_voters = None
        self.ballots_cast = None
        self._result_jurisdictions = []
        self._result_jurisdiction_lookup = {}
        self._contests = []

    def parse(self, f):
        tree = etree.parse(f)
        election_voter_turnout = self._parse_election_voter_turnout(tree)
        self.timestamp = self._parse_timestamp(tree)
        self.election_name = self._parse_election_name(tree)
        self.election_date = self._parse_election_date(tree)
        self.region = self._parse_region(tree)
        self.total_voters = int(election_voter_turnout[0])
        self.ballots_cast = int(election_voter_turnout[1])
        self.voter_turnout = float(election_voter_turnout[2])

        self._result_jurisdictions = self._parse_result_jurisdictions(tree)
        self._result_jurisdiction_lookup = {p.name: p for p in self._result_jurisdictions}
        self._contests = self._parse_contests(tree, self._result_jurisdiction_lookup)

    def _parse_timestamp(self, tree):
        return dateutil.parser.parse(tree.xpath('/ElectionResult/Timestamp')[0].text)

    def _parse_election_name(self, tree):
        return tree.xpath('/ElectionResult/ElectionName')[0].text

    def _parse_election_date(self, tree):
        dt = datetime.datetime.strptime(tree.xpath('/ElectionResult/ElectionDate')[0].text, '%m/%d/%Y')
        return datetime.date(dt.year, dt.month, dt.day)

    def _parse_region(self, tree):
        return tree.xpath('/ElectionResult/Region')[0].text

    def _parse_election_voter_turnout(self, tree):
        els = tree.xpath('/ElectionResult/VoterTurnout') + tree.xpath('/ElectionResult/ElectionVoterTurnout')
        return els[0].values()

    def _parse_result_jurisdictions(self, tree):
        result_jurisdictions = []
        precinct_els = tree.xpath('/ElectionResult/VoterTurnout/Precincts/Precinct')
        for el in precinct_els:
            result_jurisdictions.append(ResultJurisdiction(
              name=el.attrib['name'],
              total_voters=int(el.attrib['totalVoters']),
              ballots_cast=int(el.attrib['ballotsCast']),
              voter_turnout=float(el.attrib['voterTurnout']),
              percent_reporting=float(el.attrib['percentReporting']),
              precincts_participating=None,
              precincts_reported=None,
              precincts_reporting_percent=None,
              level='precinct'
            ))
        county_els = tree.xpath('/ElectionResult/ElectionVoterTurnout/Counties/County')
        for el in county_els:
            result_jurisdictions.append(ResultJurisdiction(
              name=el.attrib['name'],
              total_voters=int(el.attrib['totalVoters']),
              ballots_cast=int(el.attrib['ballotsCast']),
              voter_turnout=float(el.attrib['voterTurnout']),
              percent_reporting=None,
              precincts_participating=float(el.attrib['precinctsParticipating']),
              precincts_reported=float(el.attrib['precinctsReported']),
              precincts_reporting_percent=float(el.attrib['precinctsReportingPercent']),
              level='county'
            ))
        return result_jurisdictions

    @property
    def result_jurisdictions(self):
        return self._result_jurisdictions

    @property
    def contests(self):
        return self._contests

    @property
    def results(self):
        results = []
        for c in self.contests:
            results.extend(c.results)
        return results

    def _get_attrib(self, el, key, fn=None):
        try:
            val = el.attrib[key]
            if fn is not None:
                val = fn(val)
            return val
        except KeyError:
            return None

    def _parse_contests(self, tree, result_jurisdiction_lookup):
        contest_els = tree.xpath('/ElectionResult/Contest')
        return [self._parse_contest(el, result_jurisdiction_lookup) for el in contest_els]

    def _parse_contest(self, el, result_jurisdiction_lookup):
        contest = Contest(
           key=self._get_attrib(el, 'key'),
           text=self._get_attrib(el, 'text'),
           vote_for=self._get_attrib(el, 'voteFor', int),
           is_question=self._get_attrib(el, 'isQuestion', self._parse_boolean),
           precincts_reporting=self._get_attrib(el,'precinctsReporting', int),
           precincts_reported=self._get_attrib(el, 'precinctsReported', int),
           precincts_participating=self._get_attrib(el, 'precinctsParticipating', int),
           counties_reported=self._get_attrib(el, 'countiesReported', int),
           counties_participating=self._get_attrib(el, 'countiesParticipating', int)
        )

        for r in self._parse_no_choice_results(el, result_jurisdiction_lookup, contest):
            contest.add_result(r)

        for c in self._parse_choices(el, result_jurisdiction_lookup, contest):
            contest.add_choice(c)

        return contest

    def _parse_no_choice_results(self, el, result_jurisdiction_lookup, contest):
        results = []
        vote_type_els = el.xpath('./VoteType')
        for vt_el in vote_type_els:
            vote_type = vt_el.attrib['name']
            results.append(Result(
                contest=contest,
                vote_type=vote_type,
                jurisdiction=None,
                votes=int(vt_el.attrib['votes']),
                choice=None
            ))
            for precinct_el in vt_el.xpath('./Precinct'):
                precinct = result_jurisdiction_lookup[precinct_el.attrib['name']]
                results.append(Result(
                    contest=contest,
                    vote_type=vote_type,
                    jurisdiction=precinct,
                    votes=int(precinct_el.attrib['votes']),
                    choice=None
                ))

            for county_el in vt_el.xpath('./County'):
                choice.add_result(Result(
                    contest=contest,
                    vote_type=vote_type,
                    jurisdiction=county_el.attrib['name'],
                    votes=int(precinct_el.attrib['votes']),
                    choice=None
                ))

        return results

    def _parse_choices(self, el, result_jurisdiction_lookup, contest):
        return [self._parse_choice(c_el, result_jurisdiction_lookup, contest)
                for c_el in el.xpath('Choice')]

    def _parse_choice(self, el, result_jurisdiction_lookup, contest):
        choice = Choice(
            contest=contest,
            key=el.attrib['key'],
            text=el.attrib['text'],
            total_votes=el.attrib['totalVotes'],
        )
        for vt_el in el.xpath('./VoteType'):
            vote_type = vt_el.attrib['name']
            choice.add_result(Result(
              contest=contest,
              vote_type=vote_type,
              jurisdiction=None,
              votes=int(vt_el.attrib['votes']),
              choice=choice
            ))

            for precinct_el in vt_el.xpath('./Precinct'):
                precinct = result_jurisdiction_lookup[precinct_el.attrib['name']]
                choice.add_result(Result(
                    contest=contest,
                    vote_type=vote_type,
                    jurisdiction=precinct,
                    votes=int(precinct_el.attrib['votes']),
                    choice=choice
                ))

            for county_el in vt_el.xpath('./County'):
                choice.add_result(Result(
                    contest=contest,
                    vote_type=vote_type,
                    jurisdiction=county_el.attrib['name'],
                    votes=int(county_el.attrib['votes']),
                    choice=choice
                ))

        return choice

    def _parse_boolean(self, s):
        return s == "true"

class ResultJurisdiction(namedtuple('ResultJurisdiction', ['name', 'total_voters', 'ballots_cast',
        'voter_turnout', 'percent_reporting', 'precincts_participating', 'precincts_reported',
        'precincts_reporting_percent', 'level'])):
    def __str__(self):
        return self.name

class Contest(namedtuple('Contest', ['key', 'text', 'vote_for', 'is_question',
        'precincts_reporting', 'precincts_participating', 'precincts_reported',
        'counties_participating', 'counties_reported'])):
    def __init__(self, *args, **kwargs):
        super(Contest, self).__init__(*args, **kwargs)
        self._choices = []
        self._results = []

    def __str__(self):
        return self.text

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

    def __str__(self):
        return self.text

    @property
    def results(self):
        return self._results

    def add_result(self, r):
        self._results.append(r)

Result = namedtuple('Result', ['contest', 'vote_type', 'jurisdiction', 'votes', 'choice'])
