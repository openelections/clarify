import datetime
import unittest

from clarify.parser import Parser

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

        result_jurisdiction_name = "A105"
        result_jurisdiction = er.get_result_jurisdiction(result_jurisdiction_name)

        self.assertEqual(str(result_jurisdiction), result_jurisdiction_name)
        self.assertEqual(result_jurisdiction.name, result_jurisdiction_name)
        self.assertEqual(result_jurisdiction.total_voters, 0)
        self.assertEqual(result_jurisdiction.ballots_cast, 171)
        self.assertEqual(result_jurisdiction.voter_turnout, 0)
        self.assertEqual(result_jurisdiction.percent_reporting, 4)

        self.assertEqual(result_jurisdiction, precinct)

        contest_text = "US Senator - REPUBLICAN"
        contest = er.get_contest(contest_text)

        self.assertEqual(str(contest), contest_text)
        self.assertEqual(contest.text, contest_text)
        self.assertEqual(contest.key, "4")
        self.assertEqual(contest.vote_for, 1)
        self.assertFalse(contest.is_question)
        self.assertEqual(contest.precincts_reporting, 32)
        self.assertEqual(contest.precincts_reported, 32)

        contest_choice_text = "Matt BEVIN"
        contest_choice = contest.choices[0]

        self.assertEqual(contest_choice.contest, contest)

        self.assertEqual(str(contest_choice), contest_choice_text)
        self.assertEqual(contest_choice.text, contest_choice_text)
        self.assertEqual(contest_choice.key, "1")
        self.assertEqual(contest_choice.total_votes, 820)


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

        result_jurisdiction_name = "Arkansas"
        result_jurisdiction = er.get_result_jurisdiction(result_jurisdiction_name)

        self.assertEqual(str(result_jurisdiction), result_jurisdiction_name)
        self.assertEqual(result_jurisdiction.name, result_jurisdiction_name)
        self.assertEqual(result_jurisdiction.total_voters, 10196)
        self.assertEqual(result_jurisdiction.ballots_cast, 5137)
        self.assertEqual(result_jurisdiction.voter_turnout, 50.38)
        self.assertEqual(result_jurisdiction.precincts_participating, 30)
        self.assertEqual(result_jurisdiction.precincts_reported, 30)
        self.assertEqual(result_jurisdiction.precincts_reporting_percent, 100.0)

        self.assertEqual(result_jurisdiction, county)

        contest_text = "U.S. Senate"
        contest = er.get_contest(contest_text)

        self.assertEqual(str(contest), contest_text)
        self.assertEqual(contest.text, contest_text)
        self.assertEqual(contest.key, "100")
        self.assertEqual(contest.vote_for, 1)
        self.assertFalse(contest.is_question)
        self.assertEqual(contest.counties_participating, 75)
        self.assertEqual(contest.counties_reported, 75)
        self.assertEqual(contest.precincts_participating, 2655)
        self.assertEqual(contest.precincts_reported, 2655)

        contest_choice_text = "Tom Cotton"
        contest_choice = contest.choices[0]

        self.assertEqual(contest_choice.contest, contest)

        self.assertEqual(str(contest_choice), contest_choice_text)
        self.assertEqual(contest_choice.text, contest_choice_text)
        self.assertEqual(contest_choice.key, "001")
        self.assertEqual(contest_choice.party, "REP")
        self.assertEqual(contest_choice.total_votes, 477734)

