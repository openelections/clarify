import datetime
import unittest

from clarity.parser import JurisdictionResults

TEST_XML = """<?xml version="1.0"?>
<!--Election result snapshot imported from Tabulation System
-->
<ElectionResult>
    <Timestamp>5/20/2014 8:19:21 PM EDT</Timestamp>
    <ElectionName>2014 Primary Election</ElectionName>
    <ElectionDate>5/20/2014</ElectionDate>
    <Region>Greenup</Region>
    <VoterTurnout totalVoters="28162" ballotsCast="5926" voterTurnout="21.04">
        <Precincts>
            <Precinct name="AB" totalVoters="0" ballotsCast="203" voterTurnout="0.00" percentReporting="32" />
            <Precinct name="A101" totalVoters="0" ballotsCast="157" voterTurnout="0.00" percentReporting="4" />
            <Precinct name="A102" totalVoters="0" ballotsCast="207" voterTurnout="0.00" percentReporting="4" />
            <Precinct name="A103" totalVoters="0" ballotsCast="133" voterTurnout="0.00" percentReporting="4" />
            <Precinct name="A104" totalVoters="0" ballotsCast="124" voterTurnout="0.00" percentReporting="4" />
            <Precinct name="A105" totalVoters="0" ballotsCast="171" voterTurnout="0.00" percentReporting="4" />
            <Precinct name="A106" totalVoters="0" ballotsCast="139" voterTurnout="0.00" percentReporting="4" />
            <Precinct name="A107" totalVoters="0" ballotsCast="218" voterTurnout="0.00" percentReporting="4" />
            <Precinct name="A108" totalVoters="0" ballotsCast="134" voterTurnout="0.00" percentReporting="4" />
            <Precinct name="A109" totalVoters="0" ballotsCast="285" voterTurnout="0.00" percentReporting="4" />
            <Precinct name="A111" totalVoters="0" ballotsCast="125" voterTurnout="0.00" percentReporting="4" />
            <Precinct name="A112" totalVoters="0" ballotsCast="287" voterTurnout="0.00" percentReporting="4" />
            <Precinct name="B101" totalVoters="0" ballotsCast="148" voterTurnout="0.00" percentReporting="4" />
            <Precinct name="B102" totalVoters="0" ballotsCast="94" voterTurnout="0.00" percentReporting="4" />
            <Precinct name="B103" totalVoters="0" ballotsCast="251" voterTurnout="0.00" percentReporting="4" />
            <Precinct name="B104" totalVoters="0" ballotsCast="128" voterTurnout="0.00" percentReporting="4" />
            <Precinct name="B105" totalVoters="0" ballotsCast="162" voterTurnout="0.00" percentReporting="4" />
            <Precinct name="B106" totalVoters="0" ballotsCast="86" voterTurnout="0.00" percentReporting="4" />
            <Precinct name="B107" totalVoters="0" ballotsCast="199" voterTurnout="0.00" percentReporting="4" />
            <Precinct name="B108" totalVoters="0" ballotsCast="293" voterTurnout="0.00" percentReporting="4" />
            <Precinct name="B109" totalVoters="0" ballotsCast="96" voterTurnout="0.00" percentReporting="4" />
            <Precinct name="B110" totalVoters="0" ballotsCast="110" voterTurnout="0.00" percentReporting="4" />
            <Precinct name="B111" totalVoters="0" ballotsCast="256" voterTurnout="0.00" percentReporting="4" />
            <Precinct name="C101" totalVoters="0" ballotsCast="164" voterTurnout="0.00" percentReporting="4" />
            <Precinct name="C102" totalVoters="0" ballotsCast="204" voterTurnout="0.00" percentReporting="4" />
            <Precinct name="C103" totalVoters="0" ballotsCast="153" voterTurnout="0.00" percentReporting="4" />
            <Precinct name="C104" totalVoters="0" ballotsCast="327" voterTurnout="0.00" percentReporting="4" />
            <Precinct name="C105" totalVoters="0" ballotsCast="192" voterTurnout="0.00" percentReporting="4" />
            <Precinct name="C106" totalVoters="0" ballotsCast="219" voterTurnout="0.00" percentReporting="4" />
            <Precinct name="C107" totalVoters="0" ballotsCast="86" voterTurnout="0.00" percentReporting="4" />
            <Precinct name="C108" totalVoters="0" ballotsCast="195" voterTurnout="0.00" percentReporting="4" />
            <Precinct name="C109" totalVoters="0" ballotsCast="169" voterTurnout="0.00" percentReporting="4" />
            <Precinct name="C110" totalVoters="0" ballotsCast="211" voterTurnout="0.00" percentReporting="4" />
        </Precincts>
    </VoterTurnout>
    <Contest key="4" text="US Senator - REPUBLICAN" voteFor="1" isQuestion="false" precinctsReporting="32" precinctsReported="32">
        <VoteType name="Undervotes" votes="0">
            <Precinct name="AB" votes="0" />
            <Precinct name="A101" votes="0" />
            <Precinct name="A102" votes="0" />
            <Precinct name="A103" votes="0" />
            <Precinct name="A104" votes="0" />
            <Precinct name="A105" votes="0" />
            <Precinct name="A106" votes="0" />
            <Precinct name="A107" votes="0" />
            <Precinct name="A108" votes="0" />
            <Precinct name="A109" votes="0" />
            <Precinct name="A111" votes="0" />
            <Precinct name="A112" votes="0" />
            <Precinct name="B101" votes="0" />
            <Precinct name="B102" votes="0" />
            <Precinct name="B103" votes="0" />
            <Precinct name="B104" votes="0" />
            <Precinct name="B105" votes="0" />
            <Precinct name="B106" votes="0" />
            <Precinct name="B107" votes="0" />
            <Precinct name="B108" votes="0" />
            <Precinct name="B109" votes="0" />
            <Precinct name="B110" votes="0" />
            <Precinct name="B111" votes="0" />
            <Precinct name="C101" votes="0" />
            <Precinct name="C102" votes="0" />
            <Precinct name="C103" votes="0" />
            <Precinct name="C104" votes="0" />
            <Precinct name="C105" votes="0" />
            <Precinct name="C106" votes="0" />
            <Precinct name="C107" votes="0" />
            <Precinct name="C108" votes="0" />
            <Precinct name="C109" votes="0" />
            <Precinct name="C110" votes="0" />
        </VoteType>
        <VoteType name="Overvotes" votes="0">
            <Precinct name="AB" votes="0" />
            <Precinct name="A101" votes="0" />
            <Precinct name="A102" votes="0" />
            <Precinct name="A103" votes="0" />
            <Precinct name="A104" votes="0" />
            <Precinct name="A105" votes="0" />
            <Precinct name="A106" votes="0" />
            <Precinct name="A107" votes="0" />
            <Precinct name="A108" votes="0" />
            <Precinct name="A109" votes="0" />
            <Precinct name="A111" votes="0" />
            <Precinct name="A112" votes="0" />
            <Precinct name="B101" votes="0" />
            <Precinct name="B102" votes="0" />
            <Precinct name="B103" votes="0" />
            <Precinct name="B104" votes="0" />
            <Precinct name="B105" votes="0" />
            <Precinct name="B106" votes="0" />
            <Precinct name="B107" votes="0" />
            <Precinct name="B108" votes="0" />
            <Precinct name="B109" votes="0" />
            <Precinct name="B110" votes="0" />
            <Precinct name="B111" votes="0" />
            <Precinct name="C101" votes="0" />
            <Precinct name="C102" votes="0" />
            <Precinct name="C103" votes="0" />
            <Precinct name="C104" votes="0" />
            <Precinct name="C105" votes="0" />
            <Precinct name="C106" votes="0" />
            <Precinct name="C107" votes="0" />
            <Precinct name="C108" votes="0" />
            <Precinct name="C109" votes="0" />
            <Precinct name="C110" votes="0" />
        </VoteType>
        <Choice key="1" text="Matt BEVIN" totalVotes="820">
            <VoteType name="Election" votes="820">
                <Precinct name="AB" votes="29" />
                <Precinct name="A101" votes="36" />
                <Precinct name="A102" votes="25" />
                <Precinct name="A103" votes="10" />
                <Precinct name="A104" votes="15" />
                <Precinct name="A105" votes="16" />
                <Precinct name="A106" votes="16" />
                <Precinct name="A107" votes="22" />
                <Precinct name="A108" votes="17" />
                <Precinct name="A109" votes="52" />
                <Precinct name="A111" votes="16" />
                <Precinct name="A112" votes="47" />
                <Precinct name="B101" votes="30" />
                <Precinct name="B102" votes="23" />
                <Precinct name="B103" votes="58" />
                <Precinct name="B104" votes="16" />
                <Precinct name="B105" votes="29" />
                <Precinct name="B106" votes="10" />
                <Precinct name="B107" votes="28" />
                <Precinct name="B108" votes="20" />
                <Precinct name="B109" votes="18" />
                <Precinct name="B110" votes="12" />
                <Precinct name="B111" votes="30" />
                <Precinct name="C101" votes="24" />
                <Precinct name="C102" votes="33" />
                <Precinct name="C103" votes="20" />
                <Precinct name="C104" votes="27" />
                <Precinct name="C105" votes="25" />
                <Precinct name="C106" votes="41" />
                <Precinct name="C107" votes="9" />
                <Precinct name="C108" votes="23" />
                <Precinct name="C109" votes="19" />
                <Precinct name="C110" votes="24" />
            </VoteType>
        </Choice>
        <Choice key="2" text="Brad COPAS" totalVotes="11">
            <VoteType name="Election" votes="11">
                <Precinct name="AB" votes="0" />
                <Precinct name="A101" votes="0" />
                <Precinct name="A102" votes="1" />
                <Precinct name="A103" votes="0" />
                <Precinct name="A104" votes="1" />
                <Precinct name="A105" votes="0" />
                <Precinct name="A106" votes="0" />
                <Precinct name="A107" votes="0" />
                <Precinct name="A108" votes="1" />
                <Precinct name="A109" votes="0" />
                <Precinct name="A111" votes="0" />
                <Precinct name="A112" votes="0" />
                <Precinct name="B101" votes="0" />
                <Precinct name="B102" votes="0" />
                <Precinct name="B103" votes="0" />
                <Precinct name="B104" votes="0" />
                <Precinct name="B105" votes="0" />
                <Precinct name="B106" votes="0" />
                <Precinct name="B107" votes="0" />
                <Precinct name="B108" votes="0" />
                <Precinct name="B109" votes="0" />
                <Precinct name="B110" votes="0" />
                <Precinct name="B111" votes="0" />
                <Precinct name="C101" votes="0" />
                <Precinct name="C102" votes="0" />
                <Precinct name="C103" votes="0" />
                <Precinct name="C104" votes="2" />
                <Precinct name="C105" votes="0" />
                <Precinct name="C106" votes="5" />
                <Precinct name="C107" votes="0" />
                <Precinct name="C108" votes="1" />
                <Precinct name="C109" votes="0" />
                <Precinct name="C110" votes="0" />
            </VoteType>
        </Choice>
        <Choice key="3" text="Mitch McCONNELL" totalVotes="1135">
            <VoteType name="Election" votes="1135">
                <Precinct name="AB" votes="35" />
                <Precinct name="A101" votes="22" />
                <Precinct name="A102" votes="45" />
                <Precinct name="A103" votes="30" />
                <Precinct name="A104" votes="28" />
                <Precinct name="A105" votes="28" />
                <Precinct name="A106" votes="19" />
                <Precinct name="A107" votes="47" />
                <Precinct name="A108" votes="19" />
                <Precinct name="A109" votes="75" />
                <Precinct name="A111" votes="20" />
                <Precinct name="A112" votes="74" />
                <Precinct name="B101" votes="11" />
                <Precinct name="B102" votes="8" />
                <Precinct name="B103" votes="27" />
                <Precinct name="B104" votes="22" />
                <Precinct name="B105" votes="21" />
                <Precinct name="B106" votes="12" />
                <Precinct name="B107" votes="33" />
                <Precinct name="B108" votes="44" />
                <Precinct name="B109" votes="14" />
                <Precinct name="B110" votes="26" />
                <Precinct name="B111" votes="28" />
                <Precinct name="C101" votes="56" />
                <Precinct name="C102" votes="39" />
                <Precinct name="C103" votes="29" />
                <Precinct name="C104" votes="89" />
                <Precinct name="C105" votes="52" />
                <Precinct name="C106" votes="39" />
                <Precinct name="C107" votes="18" />
                <Precinct name="C108" votes="63" />
                <Precinct name="C109" votes="36" />
                <Precinct name="C110" votes="26" />
            </VoteType>
        </Choice>
        <Choice key="4" text="Chris PAYNE" totalVotes="48">
            <VoteType name="Election" votes="48">
                <Precinct name="AB" votes="3" />
                <Precinct name="A101" votes="2" />
                <Precinct name="A102" votes="4" />
                <Precinct name="A103" votes="0" />
                <Precinct name="A104" votes="1" />
                <Precinct name="A105" votes="1" />
                <Precinct name="A106" votes="2" />
                <Precinct name="A107" votes="0" />
                <Precinct name="A108" votes="0" />
                <Precinct name="A109" votes="2" />
                <Precinct name="A111" votes="1" />
                <Precinct name="A112" votes="2" />
                <Precinct name="B101" votes="2" />
                <Precinct name="B102" votes="1" />
                <Precinct name="B103" votes="2" />
                <Precinct name="B104" votes="0" />
                <Precinct name="B105" votes="1" />
                <Precinct name="B106" votes="1" />
                <Precinct name="B107" votes="2" />
                <Precinct name="B108" votes="1" />
                <Precinct name="B109" votes="0" />
                <Precinct name="B110" votes="3" />
                <Precinct name="B111" votes="1" />
                <Precinct name="C101" votes="3" />
                <Precinct name="C102" votes="3" />
                <Precinct name="C103" votes="2" />
                <Precinct name="C104" votes="0" />
                <Precinct name="C105" votes="2" />
                <Precinct name="C106" votes="3" />
                <Precinct name="C107" votes="1" />
                <Precinct name="C108" votes="1" />
                <Precinct name="C109" votes="1" />
                <Precinct name="C110" votes="0" />
            </VoteType>
        </Choice>
        <Choice key="5" text="Shawna STERLING" totalVotes="46">
            <VoteType name="Election" votes="46">
                <Precinct name="AB" votes="0" />
                <Precinct name="A101" votes="0" />
                <Precinct name="A102" votes="2" />
                <Precinct name="A103" votes="2" />
                <Precinct name="A104" votes="2" />
                <Precinct name="A105" votes="2" />
                <Precinct name="A106" votes="1" />
                <Precinct name="A107" votes="0" />
                <Precinct name="A108" votes="1" />
                <Precinct name="A109" votes="3" />
                <Precinct name="A111" votes="1" />
                <Precinct name="A112" votes="1" />
                <Precinct name="B101" votes="1" />
                <Precinct name="B102" votes="0" />
                <Precinct name="B103" votes="1" />
                <Precinct name="B104" votes="2" />
                <Precinct name="B105" votes="1" />
                <Precinct name="B106" votes="2" />
                <Precinct name="B107" votes="1" />
                <Precinct name="B108" votes="0" />
                <Precinct name="B109" votes="1" />
                <Precinct name="B110" votes="0" />
                <Precinct name="B111" votes="1" />
                <Precinct name="C101" votes="2" />
                <Precinct name="C102" votes="0" />
                <Precinct name="C103" votes="2" />
                <Precinct name="C104" votes="2" />
                <Precinct name="C105" votes="6" />
                <Precinct name="C106" votes="2" />
                <Precinct name="C107" votes="3" />
                <Precinct name="C108" votes="0" />
                <Precinct name="C109" votes="1" />
                <Precinct name="C110" votes="3" />
            </VoteType>
        </Choice>
    </Contest>
</ElectionResult>
"""
"""
One contest's election results, to speed up testing

Extracted from
http://results.enr.clarityelections.com/KY/Greenup/51018/129034/reports/detailxml.zip
"""

class TestJurisdictionResults(unittest.TestCase):
    def test_parse(self):
        num_precincts = 32
        num_candidates = 5
        # Overvotes and undervotes
        num_pseudo_candidates = 2
        num_expected_results = ((num_candidates + num_pseudo_candidates) *
            num_precincts)

        er = JurisdictionResults()
        er.parse(TEST_XML)

        self.assertEqual(er.timestamp, datetime.datetime(2014, 5, 20, 8, 19, 21))
        self.assertEqual(er.election_name, "2014 Primary Election")
        self.assertEqual(er.election_date, datetime.date(2014, 5, 20))
        self.assertEqual(er.region, "Greenup")
        self.assertEqual(er.total_voters, 28162)
        self.assertEqual(er.ballots_cast, 5926)
        self.assertEqual(er.voter_turnout, 21.04)

        self.assertEqual(len(er.precincts), num_precincts)
        precinct = next(p for p in er.precincts if p.name == 'A105')
        self.assertEqual(precinct.total_voters, 0)
        self.assertEqual(precinct.ballots_cast, 171)
        self.assertEqual(precinct.voter_turnout, 0)
        self.assertEqual(precinct.percentReporting, 4)

        #results = er.choice_results()
        #self.assertEqual(len(results), num_expected_results)
