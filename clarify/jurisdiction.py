import concurrent.futures

from six.moves.urllib import parse

import requests
from requests_futures.sessions import FuturesSession
import lxml.html
from lxml.cssselect import CSSSelector


class Jurisdiction(object):

    """
    Returns an object representing a state, county or city that has
    a Clarity election results page, and methods for retrieving
    additional information about those results.
    """

    def __init__(self, url, level, name=''):
        """
        To create an instance, pass a Clarity results URL for the top-level
        political jurisdiction (a state, for example), and the corresponding
        level in lowercase ("state" or "county").
        """

        self.url = url
        self.parsed_url = self._parse_url()
        self.state = self._get_state_from_url()
        self.level = level
        self.name = name
        self.summary_url = self._get_summary_url()

    def get_subjurisdictions(self):
        """
        Returns a list of subjurisdictions depending on the level
        of the main jurisdiction. States always have counties, and
        counties and cities may have precincts.
        """

        subjurisdictions_url = self._get_subjurisdictions_url()
        if not subjurisdictions_url:
            json_url = self.url.replace('summary.html','json/electionsettings.json')
            try:
                r = requests.get(json_url)
                r.raise_for_status()
                jurisdictions = []
                counties = r.json()['settings']['electiondetails']['participatingcounties']
                jurisdictions = self._get_subjurisdictions_urls_from_json(counties)
                return jurisdictions
            except requests.exceptions.HTTPError:
                return []
        try:
            r = requests.get(subjurisdictions_url)
            r.raise_for_status()

            # Use a maximum of 10 workers.  Should we parameterize this?
            session = FuturesSession(max_workers=10)
            future_to_name = {}
            for url, name in self._scrape_subjurisdiction_paths(r.text):
                future = self._subjurisdiction_url_future(session, url)
                future_to_name[future] = name

            jurisdictions = []
            for future in concurrent.futures.as_completed(future_to_name):
                url = self._subjurisdiction_url_from_future(future)
                name = future_to_name[future]
                jurisdictions.append(Jurisdiction(url, 'county', name))

            return jurisdictions
        except requests.exceptions.HTTPError:
            return []

    def _parse_url(self):
        """
        The parsed version of the original URL is used by several methods,
        so we assign it to self.parsed_url on init. If URL has "/Web01/"
        segment, that gets stripped out.
        """
        if 'Web01/' in self.url:
            url = self.url.replace('Web01/','')
        else:
            url = self.url
        return parse.urlsplit(url)

    def _get_subjurisdictions_urls_from_json(self, counties):
        subjurisdictions = []
        for c in counties:
            name, first_id, second_id, date, fill = c.split('|')
            url = 'http://results.enr.clarityelections.com/'+self.state+'/'+name+'/'+first_id+'/'+second_id+'/Web01/en/summary.html'
            subjurisdictions.append(Jurisdiction(url, 'county', name))
        return subjurisdictions

    def _get_state_from_url(self):
        """
        Returns the two-digit state abbreviation from the URL.
        """
        return self.parsed_url.path.split('/')[1]

    def _get_subjurisdictions_url(self):
        """
        Returns a URL for the county detail page, which lists URLs for
        each of the counties in a state. If original jurisdiction is
        not a state, returns None.
        """
        if self.level != 'state':
            return None
        elif 'Web01/' in self.url:
            return None
        else:
            newpath = '/'.join(self.parsed_url.path.split('/')[:-1]) + '/select-county.html'
            parts = (self.parsed_url.scheme, self.parsed_url.netloc, newpath, self.parsed_url.query,
                     self.parsed_url.fragment)
            return parse.urlunsplit(parts)

    def _scrape_subjurisdiction_paths(self, html):
        """
        Parse subjurisdictions_url to find paths for counties.
        """
        tree = lxml.html.fromstring(html)
        sel = CSSSelector('ul li a')
        results = sel(tree)
        return [(match.get('value'), match.get('id')) for match in results]

    def _subjurisdiction_url_future(self, session, path):
        url = self._state_url() + "/".join(path.split('/')[:3])
        # Make sure path ends with '/'
        # While the URL without the trailing forward slash will ultimately
        # resolve to the same place, it causes a redirect which means an
        # extra request.
        if not url.endswith('/'):
            url = url + '/'
        future = session.get(url)
        return future

    def _subjurisdiction_url_from_future(self, future):
        res = future.result()
        url = res.url
        redirect_path = self._scrape_subjurisdiction_summary_path(res.text)
        # We need to strip the trailing '/' from the URL before adding
        # the additional path
        return url.strip('/') + redirect_path

    def _state_url(self):
        """
        Returns base URL used by _subjurisdiction_url.
        """
        return 'http://results.enr.clarityelections.com/' + self.state

    @classmethod
    def _scrape_subjurisdiction_summary_path(cls, html):
        """
        Checks county page for redirect path segment and returns it.
        There are two types of pages: one with segment in meta tag
        and the other with segment in script tag.
        """
        tree = lxml.html.fromstring(html)
        try:
            segment = tree.xpath("//meta[@content]")[0].values()[1].split("=")[1].split('/')[1]
        except:
            segment = tree.xpath("//script")[0].values()[0].split('/')[1]
        return '/'+ segment + '/en/summary.html'

    def report_url(self, fmt):
        """
        Returns link to detailed report depending on format. Formats are xls, txt and xml.
        """
        url = self._state_url() + '/' + '/'.join(self.parsed_url.path.split('/')[2:-2]) + "/reports/detail{}.zip".format(fmt)
        r = requests.get(url)
        if r.status_code == 200:
            return url
        else:
            return None

    def _get_summary_url(self):
        """
        Returns the summary report URL for a jurisdiction.
        """
        url = self._state_url() + '/' + '/'.join(self.parsed_url.path.split('/')[2:-2]) + "/reports/summary.zip"
        r = requests.get(url)
        if r.status_code == 200:
            return url
        else:
            return None
