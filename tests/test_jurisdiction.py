from unittest import TestCase

from clarity.jurisdiction import Jurisdiction

class TestJurisdiction(TestCase):
    def test_construct(self):
        url = 'http://results.enr.clarityjurisdictions.com/KY/15261/30235/en/summary.html'
        jurisdiction = Jurisdiction(url=url, level='state')
        self.assertEqual(jurisdiction.url, url)

    def test_get_subjurisdictions_state(self):
        # subjurisdiction url path is in script tag
        # Construct a Jurisdiction for Kentucky's 2014 Primary Election
        url = 'http://results.enr.clarityelections.com/KY/50972/131636/en/summary.html'
        jurisdiction = Jurisdiction(url=url, level='state')
        jurisdictions = jurisdiction.get_subjurisdictions()
        # Kentucky has 120 counties
        expected_jurisdiction_count = 120
        self.assertEqual(len(jurisdictions), expected_jurisdiction_count)
        for jurisdiction in jurisdictions:
            # The sub-jurisdictions of a state are counties
            self.assertEqual(jurisdiction.level, 'county')
            # The sub-jurisdictions should have a url attribute set
            self.assertIsNotNone(jurisdiction.url)

    def test_get_subjurisdictions_state_meta(self):
        # subjurisdiction url path is in meta tag
        # Construct a Jurisdiction for Kentucky's 2010 Primary Election
        url = 'http://results.enr.clarityelections.com/KY/15261/30235/en/summary.html'
        jurisdiction = Jurisdiction(url=url, level='state')
        jurisdictions = jurisdiction.get_subjurisdictions()
        # Kentucky has 120 counties
        expected_jurisdiction_count = 120
        self.assertEqual(len(jurisdictions), expected_jurisdiction_count)
        for jurisdiction in jurisdictions:
            # The sub-jurisdictions of a state are counties
            self.assertEqual(jurisdiction.level, 'county')
            # The sub-jurisdictions should have a url attribute set
            self.assertIsNotNone(jurisdiction.url)

    def test_get_sub_jurisdictions_none(self):
        """A jurisdiction with no sub-jurisdictions should return an empty list"""
        # Construct a Jurisdiction for Rockford City, IL 2014 General Election
        url = 'http://results.enr.clarityelections.com/IL/Rockford/54234/148685/en/summary.html'
        jurisdiction = Jurisdiction(url=url, level='city')
        jurisdictions = jurisdiction.get_subjurisdictions()
        # A city has no sub-jurisdictions with results
        expected_jurisdiction_count = 0
        self.assertEqual(len(jurisdictions), expected_jurisdiction_count)

    def test_detail_xml_url(self):
        # Construct a Jurisdiction for Appling County, GA 2014 Primary Election
        url = 'http://results.enr.clarityelections.com/GA/Appling/52178/139522/en/summary.html'
        jurisdiction = Jurisdiction(url=url, level='county')
        expected_url = 'http://results.enr.clarityelections.com/GA/Appling/52178/139522/reports/detailxml.zip'
        self.assertEqual(jurisdiction.detail_xml_url, expected_url)
