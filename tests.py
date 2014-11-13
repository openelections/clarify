from unittest import TestCase

from clarity import Jurisdiction

class TestJurisdiction(TestCase):
    def test_construct(self):
        url = 'http://results.enr.clarityelections.com/KY/15261/30235/en/summary.html'
        election = Jurisdiction(url=url, level='state')
        self.assertEqual(election.url, url)

    def test_get_sub_jurisdictions_state(self):
        url = ''
        election = Jurisdiction(url=url)
        jurisdictions = election.get_sub_jurisdictions()
        expected_jurisdictions = 900
        self.assertEqual(len(jurisdictions), expected_jurisdictions)
        for jurisdiction in jurisdictions:
            self.assertEqual(jurisdiction.level, 'county')

    def test_get_sub_jurisdictions_none(self):
        """A jurisdiction with no sub-jurisdictions should return an empty list"""
        url = ''
        election = Jurisdiction(url=url, level='city')
        jurisdictions = election.get_sub_jurisdictions()
        expected_jurisdictions = 0
        self.assertEqual(len(jurisdictions), expected_jurisdictions)
    
    def test_detail_xml_url(self):
        url = ''
        jurisdiction = Jurisdiction(url=url, level='county')
        expected_url = ''
        self.assertEqual(jurisdiction.detail_xml_url(), expected_url)
