import datetime
import unittest

from clarity.parser import Parser

class TestPrecinctParser(unittest.TestCase):
    def test_parse(self):
        num_precincts = 33
        num_candidates = 5
        # Overvotes and undervotes
        num_pseudo_candidates = 2
        num_expected_results = (num_candidates * (num_precincts + 1) +
                num_pseudo_candidates * (num_precincts + 1))

        er = Parser()
        er.parse('tests/data/precinct.xml')

        self.assertEqual(er.timestamp.replace(tzinfo=None), datetime.datetime(2014, 5, 20, 20, 19, 21))
        self.assertEqual(er.election_name, "2014 Primary Election")
        self.assertEqual(er.election_date, datetime.date(2014, 5, 20))
        self.assertEqual(er.region, "Greenup")
        self.assertEqual(er.total_voters, 28162)
        self.assertEqual(er.ballots_cast, 5926)
        self.assertEqual(er.voter_turnout, 21.04)

        self.assertEqual(len(er.result_jurisdictions), num_precincts)
        precinct = next(p for p in er.result_jurisdictions if p.name == 'A105')
        self.assertEqual(precinct.total_voters, 0)
        self.assertEqual(precinct.ballots_cast, 171)
        self.assertEqual(precinct.voter_turnout, 0)
        self.assertEqual(precinct.percent_reporting, 4)

        self.assertEqual(len(er.contests), 1)

        self.assertEqual(len(er.results), num_expected_results)

class TestCountyParser(unittest.TestCase):

    def test_parse(self):
        num_counties = 75
        num_candidates = 1
        # Election
        num_vote_types = 4
        num_expected_results = (num_vote_types * num_counties * num_candidates) + (num_vote_types * num_candidates)

        er = Parser()
        er.parse('tests/data/county.xml')

        self.assertEqual(er.timestamp.replace(tzinfo=None), datetime.datetime(2014, 11, 13, 14, 58, 41))
        self.assertEqual(er.election_name, "2014 General Election")
        self.assertEqual(er.election_date, datetime.date(2014, 11, 4))
        self.assertEqual(er.region, "AR")
        self.assertEqual(er.total_voters, 1690577)
        self.assertEqual(er.ballots_cast, 850615)
        self.assertEqual(er.voter_turnout, 50.32)

        self.assertEqual(len(er.result_jurisdictions), num_counties)
        county = next(c for c in er.result_jurisdictions if c.name == 'Arkansas')
        self.assertEqual(county.total_voters, 10196)
        self.assertEqual(county.ballots_cast, 5137)
        self.assertEqual(county.voter_turnout, 50.38)
        self.assertEqual(county.precincts_participating, 30)
        self.assertEqual(county.precincts_reporting_percent, 100.0)

        self.assertEqual(len(er.contests), 1)

        self.assertEqual(len(er.results), num_expected_results)
