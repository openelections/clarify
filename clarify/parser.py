import datetime
from collections import namedtuple

import dateutil.parser
from lxml import etree

class Parser(object):
    """
    Parser for a jurisdiction's detail XML report files

    An example for such a file can be found at
    http://results.enr.clarityelections.com/KY/Adair/15263/27401/reports/detailxml.zip

    """
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
        self._contest_lookup = {}

    def parse(self, f):
        """
        Parse the report XML file, populating attributes

        Args:
            f: String containing filename or file-like object for the XML
               report file to be parsed.

        """
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
        self._result_jurisdiction_lookup = {j.name: j for j in self._result_jurisdictions}
        self._contests = self._parse_contests(tree, self._result_jurisdiction_lookup)
        self._contest_lookup = {c.text: c for c in self._contests}

    def _parse_timestamp(self, tree):
        """
        Parse timestamp of this results file

        Args:
            tree: ElementTree object representing the root of the parsed XML
                document

        Returns:
            datetime.datetime object representing the results timestamp, from
            the ``Timestamp`` element in the XML document

        """
        return dateutil.parser.parse(tree.xpath('/ElectionResult/Timestamp')[0].text)

    def _parse_election_name(self, tree):
        """
        Parse election name for these results

        Args:
            tree: ElementTree object representing the root of the parsed XML
                document

        Returns:
            String representing the election name, from the ``ElectionName``
            element in the XML. For example, "2012 Arkansas Primary Election".

        """
        return tree.xpath('/ElectionResult/ElectionName')[0].text

    def _parse_election_date(self, tree):
        """
        Parse election date for these results

        Args:
            tree: ElementTree object representing the root of the parsed XML
                document

        Returns:
            date object representing the election date, from the
            ``ElectionDate`` element in the XML.

        """
        dt = datetime.datetime.strptime(tree.xpath('/ElectionResult/ElectionDate')[0].text, '%m/%d/%Y')
        return datetime.date(dt.year, dt.month, dt.day)

    def _parse_region(self, tree):
        """
        Parse the region for these results

        This will generally be the name of a state or county name.

        Args:
            tree: ElementTree object representing the root of the parsed XML
                document

        Returns:
            String containing the region name for these results, from the
            ``Region`` element in the XML.

        """
        return tree.xpath('/ElectionResult/Region')[0].text

    def _parse_election_voter_turnout(self, tree):
        """
        Parse the aggregate voter turnout for these results

        Args:
            tree: ElementTree object representing the root of the parsed XML
                document

        Returns:
            List of strings representing the number of total voters, the number
            of ballots cast, and the percentage of voter turnout.  These
            should be cast to appropriate types in calling code.

        """
        els = tree.xpath('/ElectionResult/VoterTurnout') + tree.xpath('/ElectionResult/ElectionVoterTurnout')
        return els[0].values()

    def _parse_result_jurisdictions(self, tree):
        """
        Parse sub-jurisdictions for these results.

        Args:
            tree: ElementTree object representing the root of the parsed XML
                document

        Returns:
            List of ``ResultJurisdiction`` objects.

        """
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

    def get_contest(self, text):
        """
        Get a contest object by text.

        Args:
            name (text): The text of the contest. Often this describes the
                office, district and party.

        Returns:
            Contest object matching name
        """
        return self._contest_lookup[text]

    def get_result_jurisdiction(self, name):
        """
        Get a ResultJurisdiction object by name.

        Args:
            name (str): Name of the jurisdiction.

        Returns:
            ``ResultJurisdiction`` object whose ``name`` attribute matches
            ``name``.

        """
        return self._result_jurisdiction_lookup[name]

    def _get_attrib(self, el, attr, fn=None):
        """
        Get an attribute for an XML element

        This is used to prevent unneccessary branching or try/except clauses
        for parsing elements with different sets of attributes depending
        on the real-world thing it represents.

        Args:
            el: ``Element`` object representing an XML element
            attr: String containing attribute name
            fn: Function called on value to cast the attribute value
                from a string to a different type

        Returns:
            Value of element attribute, transformed through ``fn``, or
            None if the attribute does not exist.

        """
        try:
            val = el.attrib[attr]
            if fn is not None:
                val = fn(val)
            return val
        except KeyError:
            return None

    def _parse_contests(self, tree, result_jurisdiction_lookup):
        """
        Parse contests from these results

        Args:
            tree: ElementTree object representing the root of the parsed XML
                document
            result_jurisdiction_lookup: Dictionary mapping jurisdiction names to
                ``ResultJurisdiction`` objects

        Returns:
            List of ``Contest`` objects

        """
        contest_els = tree.xpath('/ElectionResult/Contest')
        return [self._parse_contest(el, result_jurisdiction_lookup) for el in contest_els]

    def _parse_contest(self, contest_el, result_jurisdiction_lookup):
        """
        Parse a single ``Contest`` element's attributes and results

        Args:
            contest_el: Element object for a ``Contest`` contest_element in the parsed XML.
            result_jurisdiction_lookup: Dictionary mapping jurisdiction names to
                ``ResultJurisdiction`` objects

        Returns:
            A ``Contest`` object with attributes parsed from the XML element.

        """
        contest = Contest(
           key=self._get_attrib(contest_el, 'key'),
           text=self._get_attrib(contest_el, 'text'),
           vote_for=self._get_attrib(contest_el, 'voteFor', int),
           is_question=self._get_attrib(contest_el, 'isQuestion', self._parse_boolean),
           precincts_reporting=self._get_attrib(contest_el,'precinctsReporting', int),
           precincts_reported=self._get_attrib(contest_el, 'precinctsReported', int),
           precincts_participating=self._get_attrib(contest_el, 'precinctsParticipating', int),
           counties_reported=self._get_attrib(contest_el, 'countiesReported', int),
           counties_participating=self._get_attrib(contest_el, 'countiesParticipating', int)
        )

        for r in self._parse_no_choice_results(contest_el, result_jurisdiction_lookup, contest):
            contest.add_result(r)

        for c in self._parse_choices(contest_el, contest, result_jurisdiction_lookup):
            contest.add_choice(c)

        return contest

    def _parse_no_choice_results(self, contest_el, result_jurisdiction_lookup, contest):
        """
        Parse results not associated with a Choice.

        These tend to represent overvotes and undervotes.

        Args:
            contest_el: Element object for a single ``Contest`` element in the XML
                document.
            result_jurisdiction_lookup: Dictionary mapping jurisdiction names to
                ``ResultJurisdiction`` objects

        Returns:
            A list of ``Result`` objects

        """
        results = []
        vote_type_els = contest_el.xpath('./VoteType')
        for vt_el in vote_type_els:
            vote_type = vt_el.attrib['name']
            # Add one result for the jurisdiction
            results.append(Result(
                contest=contest,
                vote_type=vote_type,
                jurisdiction=None,
                votes=int(vt_el.attrib['votes']),
                choice=None
            ))
            # The subjurisdiction elements are either ``Precinct`` for county or
            # city files or ``County`` for state files
            for subjurisdiction_el in vt_el.xpath('./Precinct') + vt_el.xpath('./County'):
                subjurisdiction = result_jurisdiction_lookup[subjurisdiction_el.attrib['name']]
                results.append(Result(
                    contest=contest,
                    vote_type=vote_type,
                    jurisdiction=subjurisdiction,
                    votes=int(subjurisdiction_el.attrib['votes']),
                    choice=None
                ))

        return results

    def _parse_choices(self, contest_el, contest, result_jurisdiction_lookup):
        """
        Parse ``Choice`` elements for a ``Contest`` element.

        Args:
            contest_el: Element object for a ``Contest`` contest_element in the parsed XML
            contest: ``Contest`` object corresponding to ``Contest`` element
            result_jurisdiction_lookup: Dictionary mapping jurisdiction names to
                ``ResultJurisdiction`` objects

        Returns:
            A list of ``Choice`` elements

        """
        return [self._parse_choice(c_el, contest, result_jurisdiction_lookup)
                for c_el in contest_el.xpath('Choice')]

    def _parse_choice(self, contest_el, contest, result_jurisdiction_lookup):
        """
        Parse a single ``Choice`` element

        Args:
            contest_el: Element object for a ``Contest`` contest_element in the parsed XML
            contest: ``Contest`` object corresponding to ``Contest`` element
            result_jurisdiction_lookup: Dictionary mapping jurisdiction names to
                ``ResultJurisdiction`` objects

        Returns:
            A ``Choice`` element

        """

        try:
            party=contest_el.attrib['party']
        except:
            party=None

        choice = Choice(
            contest=contest,
            key=contest_el.attrib['key'],
            text=contest_el.attrib['text'],
            party=party,
            total_votes=contest_el.attrib['totalVotes'],
        )

        for vt_el in contest_el.xpath('./VoteType'):
            vote_type = vt_el.attrib['name']
            choice.add_result(Result(
              contest=contest,
              vote_type=vote_type,
              jurisdiction=None,
              votes=int(vt_el.attrib['votes']),
              choice=choice
            ))

            for subjurisdiction_el in vt_el.xpath('./Precinct') + vt_el.xpath('./County'):
                subjurisdiction = result_jurisdiction_lookup[subjurisdiction_el.attrib['name']]
                choice.add_result(Result(
                    contest=contest,
                    vote_type=vote_type,
                    jurisdiction=subjurisdiction,
                    votes=int(subjurisdiction_el.attrib['votes']),
                    choice=choice
                ))
        return choice

    @classmethod
    def _parse_boolean(cls, s):
        """
        Convert a string representing a boolean value to a boolo

        Args:
            s: A string

        Returns:
            True if s equals "true", otherwise False

        >>> Parser._parse_boolean("true")
        True
        >>> Parser._parse_boolean("false")
        False
        >>> Parser._parse_boolean("baz")
        False

        """
        return s == "true"


class ResultAggregatorMixin(object):
    """
    Mixin class for classes that have related results
    """
    def _init_results(self):
        """Initialize the list that holds results"""
        self._results = []

    @property
    def results(self):
        """Return the list of associated Result objects"""
        return self._results

    def add_result(self, result):
        """
        Associate a ``Result`` object with this object
        """
        self._results.append(result)


RESULT_FIELDS = [
    'name',
    'total_voters',
    'ballots_cast',
    'voter_turnout',
    'percent_reporting',
    'precincts_participating',
    'precincts_reported',
    'precincts_reporting_percent',
    'level',
]


class ResultJurisdiction(ResultAggregatorMixin,
        namedtuple('ResultJurisdictionBase', RESULT_FIELDS)):
    """
    A jurisdiction such as a county or precinct that has associated results
    """
    def __new__(cls, *args, **kwargs):
        self = super(ResultJurisdiction, cls).__new__(cls, *args, **kwargs)
        self._init_results()
        return self

    def __str__(self):
        return self.name


CONTEST_FIELDS = [
    'key',
    'text',
    'vote_for',
    'is_question',
    'precincts_reporting',
    'precincts_participating',
    'precincts_reported',
    'counties_participating',
    'counties_reported',
]


class Contest(ResultAggregatorMixin, namedtuple('ContestBase', CONTEST_FIELDS)):
    """
    A contest in an election

    A contest can represent an office, but also something like a judicial
    retention question, or a referendum.

    """
    def __new__(cls, *args, **kwargs):
        self = super(Contest, cls).__new__(cls, *args, **kwargs)
        self._init_results()
        self._choices = []
        return self

    def __str__(self):
        return self.text

    @property
    def choices(self):
        """``Choice`` objects associated with this contest"""
        return self._choices

    def add_choice(self, c):
        """Associate a ``Choice`` object with this contest"""
        self._choices.append(c)
        self._results.extend(c.results)


CHOICE_FIELDS = [
    'contest',
    'key',
    'text',
    'party',
    'total_votes'
]


class Choice(ResultAggregatorMixin, namedtuple('ChoiceBase', CHOICE_FIELDS)):
    """
    A choice in an electoral contest

    This usually represents a candidate

    """
    def __new__(cls, *args, **kwargs):
        self = super(Choice, cls).__new__(cls, *args, **kwargs)
        self._init_results()
        return self

    def __str__(self):
        return self.text


RESULT_FIELDS = [
    'contest',
    'vote_type',
    'jurisdiction',
    'votes',
    'choice'
]


class Result(namedtuple('ResultBase', RESULT_FIELDS)):
    """Votes received for a choice in a contest"""
    def __new__(cls, *args, **kwargs):
        self = super(Result, cls).__new__(cls, *args, **kwargs)
        if self.jurisdiction is not None:
            # When a result is created for a Jurisdiction, add it to the
            # Jurisdiction's list of results
            self.jurisdiction.add_result(self)
        return self
