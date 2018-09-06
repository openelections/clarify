import os
import os.path
import re
from unittest import TestCase

import responses

from clarify.jurisdiction import Jurisdiction

COUNTIES_AR = [
    "Adair",
    "Allen",
    "Anderson",
    "Ballard",
    "Barren",
    "Bath",
    "Bell",
    "Boone",
    "Bourbon",
    "Boyd",
    "Boyle",
    "Bracken",
    "Breathitt",
    "Breckinridge",
    "Bullitt",
    "Butler",
    "Caldwell",
    "Calloway",
    "Campbell",
    "Carlisle",
    "Carroll",
    "Carter",
    "Casey",
    "Christian",
    "Clark",
    "Clay",
    "Clinton",
    "Crittenden",
    "Cumberland",
    "Daviess",
    "Edmonson",
    "Elliott",
    "Estill",
    "Fayette",
    "Fleming",
    "Floyd",
    "Franklin",
    "Fulton",
    "Gallatin",
    "Garrard",
    "Grant",
    "Graves",
    "Grayson",
    "Green",
    "Greenup",
    "Hancock",
    "Hardin",
    "Harlan",
    "Harrison",
    "Hart",
    "Henderson",
    "Henry",
    "Hickman",
    "Hopkins",
    "Jackson",
    "Jefferson",
    "Jessamine",
    "Johnson",
    "Kenton",
    "Knott",
    "Knox",
    "Larue",
    "Laurel",
    "Lawrence",
    "Lee",
    "Leslie",
    "Letcher",
    "Lewis",
    "Lincoln",
    "Livingston",
    "Logan",
    "Lyon",
    "Madison",
    "Magoffin",
    "Marion",
    "Marshall",
    "Martin",
    "Mason",
    "McCracken",
    "McCreary",
    "McLean",
    "Meade",
    "Menifee",
    "Mercer",
    "Metcalfe",
    "Monroe",
    "Montgomery",
    "Morgan",
    "Muhlenberg",
    "Nelson",
    "Nicholas",
    "Ohio",
    "Oldham",
    "Owen",
    "Owsley",
    "Pendleton",
    "Perry",
    "Pike",
    "Powell",
    "Pulaski",
    "Robertson",
    "Rockcastle",
    "Rowan",
    "Russell",
    "Scott",
    "Shelby",
    "Simpson",
    "Spencer",
    "Taylor",
    "Todd",
    "Trigg",
    "Trimble",
    "Union",
    "Warren",
    "Washington",
    "Wayne",
    "Webster",
    "Whitley",
    "Wolfe",
    "Woodford",
]

# IDs for county pages that ultimately resolve from
# http://results.enr.clarityelections.com/KY/50972/131636/en/select-county.html
# Seem to start at 129035 and increment by 1
COUNTY_IDS_PAIRS = {i:c for i, c in enumerate(COUNTIES_AR, start=129035)}

COUNTY_REDIRECT_URL_RE = re.compile(r'https://results.enr.clarityelections.com/(?P<state>[A-Z]{2})/(?P<county>[A-Za-z\.]+)/(?P<page_id>\d+)/')

COUNTY_URL_RE = re.compile(r'https://results.enr.clarityelections.com/(?P<state>[A-Z]{2})/(?P<county>[A-Za-z\.]+)/(?P<page_id>\d+)/(?P<page_id_2>\d+)/')

def mock_county_response_callback(req):
    m = COUNTY_REDIRECT_URL_RE.match(req.url)
    assert m is not None
    resp_body = mock_subjurisdiction_redirect_page_script(m.group('page_id'))
    return (200, {}, resp_body)

def mock_subjurisdiction_redirect_page_script(page_id):
    tpl = """<html><head>
                    <script src="./{page_id}/js/version.js" type="text/javascript"></script>
                    <script type="text/javascript">TemplateRedirect("summary.html","./{page_id}", "", "Mobile01");</script>
                    </head></html>"""
    return tpl.format(page_id=page_id)

def mock_subjurisdiction_redirect_page_meta(page_id):
    tpl = """<html><head><META HTTP-EQUIV="Refresh" CONTENT="0; URL=./{page_id}/en/summary.html"></head></html>"""
    return tpl.format(page_id=page_id)


class TestJurisdiction(TestCase):
    def test_construct(self):
        url = 'https://results.enr.clarityelections.com/KY/15261/30235/en/summary.html'
        jurisdiction = Jurisdiction(url=url, level='state')
        self.assertEqual(jurisdiction.url, url)

    @responses.activate
    def test_get_subjurisdictions_state(self):
        # subjurisdiction url path is in script tag
        # Construct a Jurisdiction for Kentucky's 2014 Primary Election
        url = 'https://results.enr.clarityelections.com/KY/50972/131636/en/summary.html'
        # Mock the response for the county list
        county_url = 'https://results.enr.clarityelections.com/KY/50972/131636/en/select-county.html'
        response_body_path = os.path.join(os.path.dirname(os.path.realpath(__file__)),
            'data', 'select-county__KY__50972__131636.html')
        with open(response_body_path) as f:
            response_body = f.read()
        responses.add(responses.GET, county_url,
                      body=response_body, status=200,
                      content_type='text/html')

        # Mock responses to URLs like
        # http://results.enr.clarityelections.com/KY/Adair/50974/
        responses.add_callback(responses.GET, COUNTY_REDIRECT_URL_RE,
            callback=mock_county_response_callback,
            content_type='text/html')

        # Initialization will fail if this connection is not allowed.
        # XXX: This is fragile, and Jurisdiction should be refactored to prevent this from being necessary.
        responses.add(responses.GET, "https://results.enr.clarityelections.com/KY/50972/131636/reports/summary.zip", status=200)

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
            # And it matches the expected pattern
            self.assertIsNotNone(COUNTY_URL_RE.match(jurisdiction.url))

    def test_scrape_subjurisdiction_summary_path(self):
        # Test HTML that uses JavaScript to redirect to the subjurisdiction
        # summary page.
        html = mock_subjurisdiction_redirect_page_script(129035)
        path = Jurisdiction._scrape_subjurisdiction_summary_path(html)
        self.assertEqual(path, "/129035/en/summary.html")

        # Test HTML that uses a meta tag to redirect to the subjurisdiction
        # summary page.
        html = mock_subjurisdiction_redirect_page_meta(27401)
        path = Jurisdiction._scrape_subjurisdiction_summary_path(html)
        self.assertEqual(path, "/27401/en/summary.html")

    def test_get_subjurisdictions_invalid(self):
        """An invalid jurisdiction should return an empty list"""
        url = "https://results.enr.clarityelections.com/FL/54234/148685/en/summary.html"
        jurisdiction = Jurisdiction(url=url, level="state")
        subjurisdictions = jurisdiction.get_subjurisdictions()
        # An invalid jurisdiction has no sub-jurisdictions with results
        expected_subjurisdiction_count = 0
        self.assertEqual(len(subjurisdictions), expected_subjurisdiction_count)

    def test_get_sub_jurisdictions_none(self):
        """A jurisdiction with no sub-jurisdictions should return an empty list"""
        # Construct a Jurisdiction for Rockford City, IL 2014 General Election
        url = 'https://results.enr.clarityelections.com/IL/Rockford/54234/148685/en/summary.html'
        jurisdiction = Jurisdiction(url=url, level='city')
        jurisdictions = jurisdiction.get_subjurisdictions()
        # A city has no sub-jurisdictions with results
        expected_jurisdiction_count = 0
        self.assertEqual(len(jurisdictions), expected_jurisdiction_count)

    def test_get_sub_jurisdictions_none_web01(self):
        """A jurisdiction with no sub-jurisdictions with Web01 in url should return an empty list"""
        # Construct a Jurisdiction for Middlesex County, NJ 2013 General Election
        url = 'https://results.enr.clarityelections.com/NJ/Middlesex/46982/117336/Web01/en/summary.html'
        jurisdiction = Jurisdiction(url=url, level='county')
        jurisdictions = jurisdiction.get_subjurisdictions()
        # A city has no sub-jurisdictions with results
        expected_jurisdiction_count = 0
        self.assertEqual(len(jurisdictions), expected_jurisdiction_count)

    @responses.activate
    def test_get_subjurisdictions_counties_web01(self):
        """A jurisdiction with sub-jurisdictions with Web01 in url should return a list of URLs"""
        # Avoid hitting all the summary URLs for each subjurisdiction.
        responses.add(
            method=responses.GET,
            url=re.compile(r"^https://results.enr.clarityelections.com/AR/(.+/[0-9]+/[0-9]+/Web01/en/summary.html|(.+/)?[0-9]+/[0-9]+/reports/summary.zip)$"),
            status=200,
        )

        # Construct a Jurisdiction for Arkansas 2014 General Election
        url = "https://results.enr.clarityelections.com/AR/53237/149294/Web01/en/summary.html"
        responses.add_passthru(url)
        responses.add_passthru(url.replace("summary.html", "json/electionsettings.json"))
        jurisdiction = Jurisdiction(url=url, level="state")

        subjurisdictions = jurisdiction.get_subjurisdictions()

        # A state like AR has county sub-jurisdictions with results
        expected_subjurisdiction_count = 75
        self.assertEqual(len(subjurisdictions), expected_subjurisdiction_count)

        # TODO: Actually check the values in subjurisdictions.

    def test_parsed_url_web01_stripped(self):
        """
        A jurisdiction with Web01 in url should have a parsed URL that
        removes "Web01" from the URL"""
        # Construct a Jurisdiction for Arkansas 2014 General Election
        url = 'https://results.enr.clarityelections.com/AR/53237/149294/Web01/en/summary.html'
        jurisdiction = Jurisdiction(url=url, level='state')
        self.assertNotIn('Web01', jurisdiction.parsed_url.path)

    def test_report_url_xml(self):
        # Construct a Jurisdiction for Appling County, GA 2014 Primary Election
        url = 'https://results.enr.clarityelections.com/GA/Appling/52178/139522/en/summary.html'
        jurisdiction = Jurisdiction(url=url, level='county')
        expected_url = 'https://results.enr.clarityelections.com/GA/Appling/52178/139522/reports/detailxml.zip'
        self.assertEqual(jurisdiction.report_url('xml'), expected_url)

    def test_report_url_txt(self):
        # Construct a Jurisdiction for Kentucky 2010 Primary Election
        url = 'https://results.enr.clarityelections.com/KY/15261/30235/en/summary.html'
        jurisdiction = Jurisdiction(url=url, level='county')
        expected_url = 'https://results.enr.clarityelections.com/KY/15261/30235/reports/detailtxt.zip'
        self.assertEqual(jurisdiction.report_url('txt'), expected_url)

    def test_report_url_xls(self):
        # Construct a Jurisdiction for Colorado 2014 General Election
        url = 'https://results.enr.clarityelections.com/CO/53335/149144/en/summary.html'
        jurisdiction = Jurisdiction(url=url, level='county')
        expected_url = 'https://results.enr.clarityelections.com/CO/53335/149144/reports/detailxls.zip'
        self.assertEqual(jurisdiction.report_url('xls'), expected_url)

    def test_report_url_fake(self):
        # Construct a Jurisdiction for Colorado 2014 General Election
        url = "https://results.enr.clarityelections.com/CO/53335/149144/en/summary.html"
        jurisdiction = Jurisdiction(url=url, level="county")
        self.assertIsNone(jurisdiction.report_url("fake"))

    def test_summary_url(self):
        # Construct a Jurisdiction for Colorado 2014 General Election
        url = 'https://results.enr.clarityelections.com/CO/53335/149144/en/summary.html'
        jurisdiction = Jurisdiction(url=url, level='state')
        expected_url = 'https://results.enr.clarityelections.com/CO/53335/149144/reports/summary.zip'
        self.assertEqual(jurisdiction.summary_url, expected_url)
