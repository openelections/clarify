import concurrent.futures

from six.moves.urllib import parse

import re
import requests
from requests_futures.sessions import FuturesSession
import lxml.html
from lxml.cssselect import CSSSelector

# base_uri is the path prefix including the folloing named groups:
# - state_id (required)
# - jurisdiction_name (optional) -- the city/county/precinct name, with URL-safe whitespace
# - election_id (required)
BASE_URL_REGEX = re.compile(r'^(?P<base_uri>/(?P<state_id>[A-Z]{2,2})/((?P<jurisdiction_name>[A-Za-z_.]+)/)?(?P<election_id>[0-9]+))/')
CLARITY_RESULTS_HOSTNAME = "results.enr.clarityelections.com"
SUPPORTED_LEVELS = ['state', 'county', 'city', 'precinct']

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
        level in lowercase ("state", "county", "city", or "precinct").
        """

        # Preliminary check for any type which is not string-like
        if url == None:
            raise TypeError('Invalid url parameter')
        try:
            # Attempt to convert to str
            url = str(url)
        except TypeError as type_error:
            raise type_error
        except ValueError as value_error:
            raise value_error
        except Exception as error:
            # If converting to str failed, raise type error
            raise TypeError('Invalid url parameter')
        if type(url) != str:
            raise TypeError('Invalid url parameter')
        # if url is an HTTP URL to Clarity Election Results
        if len(url) >= 40 and url[0:40] == 'http://' + CLARITY_RESULTS_HOSTNAME + '/':
            # Replace HTTP with HTTPS; retain the string after the URL origin
            url = 'https://' + CLARITY_RESULTS_HOSTNAME + '/' + url[40]
        # if url is not in the allowed list of supported origins
        if len(url) < 41 or url[0:41] != 'https://' + CLARITY_RESULTS_HOSTNAME + '/':
            raise ValueError('Unsupported url origin')
        self.url = url
        self.parsed_url = self._parse_url()
        self.state = self._get_state_from_url()

        if type(level) != str:
            raise TypeError('Invalid level parameter')
        level = level.lower()
        if level not in SUPPORTED_LEVELS:
            raise ValueError('Unsupported level')
        self.level = level
        self.name = name
        self.summary_url = self._get_summary_url()
        self.current_ver = self.get_current_ver(url)

    @classmethod
    def _url_ensure_trailing_slash(cls, url):
        url_parts = parse.urlsplit(url)

        # Ensure the incoming URL ends in a slash.
        if not url_parts.path.endswith("/"):
            url_parts = url_parts._replace(path=url_parts.path + "/")

        return parse.urlunsplit(url_parts)

    @classmethod
    def get_current_ver(cls, election_url):
        election_url_parts = parse.urlsplit(cls._url_ensure_trailing_slash(election_url))
        base_url_matches = BASE_URL_REGEX.match(election_url_parts.path)
        if not base_url_matches:
            return None
        base_uri = base_url_matches.group('base_uri')
        # possible version filenames
        possible_filenames = ['/current_ver.txt']
        ret = None
        for filename in possible_filenames:
            # if we have already seen a 200-status response
            if ret == None:
                election_url_parts = election_url_parts._replace(path=base_uri + filename)
                current_ver_url = parse.urlunsplit(election_url_parts)
                current_ver_response = requests.get(current_ver_url, headers={"User-Agent": "Mozilla/5.0 (platform; rv:geckoversion) Gecko/geckotrail Firefox/firefoxversion"})
                try:
                    current_ver_response.raise_for_status()
                    ret = current_ver_response.text
                except requests.exceptions.HTTPError:
                    ret = None
        return ret

    @classmethod
    def get_latest_summary_url(cls, election_url):
        election_url = cls._url_ensure_trailing_slash(election_url)
        current_ver = cls.get_current_ver(election_url)

        # If we don't have current_ver, we can't determine a summary URL.
        if current_ver is None:
            return None

        if 'Web02' in election_url or 'web.' in election_url:
            election_url_parts = parse.urlsplit(election_url)
            election_url_parts = election_url_parts._replace(path="/".join(election_url_parts.path.split('/')[:3]), fragment='')
        else:
            election_url_parts = parse.urlsplit(election_url)

        new_paths = [
            election_url_parts.path + '/' + current_ver + "/json/en/summary.json",
            election_url_parts.path + current_ver + "/Web01/en/summary.html",
            election_url_parts.path + current_ver + "/en/summary.html",
        ]

        for new_path in new_paths:
            latest_summary_url_parts = election_url_parts._replace(path=new_path)

            latest_summary_url = parse.urlunsplit(latest_summary_url_parts)

            latest_summary_url_response = requests.get(latest_summary_url, headers={"User-Agent": "Mozilla/5.0 (platform; rv:geckoversion) Gecko/geckotrail Firefox/firefoxversion"})

            try:
                latest_summary_url_response.raise_for_status()
            except requests.exceptions.HTTPError:
                continue

            return latest_summary_url

        # If none of the expected paths succeed, return None.
        return None

    def get_subjurisdictions(self):
        """
        Returns a list of subjurisdictions depending on the level
        of the main jurisdiction. States always have counties, and
        counties and cities may have precincts.
        """

        subjurisdictions_url = self._get_subjurisdictions_url()
        if 'Web02' in self.url or 'web.' in self.url:
            json_url = self.get_latest_summary_url(self.url).replace('summary.json', 'electionsettings.json')
            try:
                r = requests.get(json_url, headers={"User-Agent": "Mozilla/5.0 (platform; rv:geckoversion) Gecko/geckotrail Firefox/firefoxversion"})
                r.raise_for_status()
                jurisdictions = []
                counties = r.json()['settings']['electiondetails']['participatingcounties']
                jurisdictions = self._get_subjurisdictions_urls_from_json(counties)
                return jurisdictions
            except requests.exceptions.HTTPError:
                return []
        elif not subjurisdictions_url:
            json_url = self.url.replace('summary.html', 'json/electionsettings.json')
            try:
                r = requests.get(json_url, headers={"User-Agent": "Mozilla/5.0 (platform; rv:geckoversion) Gecko/geckotrail Firefox/firefoxversion"})
                r.raise_for_status()
                jurisdictions = []
                counties = r.json()['settings']['electiondetails']['participatingcounties']
                jurisdictions = self._get_subjurisdictions_urls_from_json(counties)
                return jurisdictions
            except requests.exceptions.HTTPError:
                json_url = self.url.replace('summary.html', 'json/en/electionsettings.json')
                try:
                    r = requests.get(json_url, headers={"User-Agent": "Mozilla/5.0 (platform; rv:geckoversion) Gecko/geckotrail Firefox/firefoxversion"})
                    r.raise_for_status()
                    jurisdictions = []
                    counties = r.json()['settings']['electiondetails']['participatingcounties']
                    jurisdictions = self._get_subjurisdictions_urls_from_json(counties)
                    return jurisdictions
                except requests.exceptions.HTTPError:
                    return []
        try:
            r = requests.get(subjurisdictions_url, headers={"User-Agent": "Mozilla/5.0 (platform; rv:geckoversion) Gecko/geckotrail Firefox/firefoxversion"})
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
            url = self.url.replace('Web01/', '')
        else:
            url = self.url
        return parse.urlsplit(url)

    def _get_subjurisdictions_urls_from_json(self, counties):
        subjurisdictions = []
        for c in counties:
            name, first_id, second_id, date, fill = c.split('|')
            url = 'https://results.enr.clarityelections.com/' + self.state + '/' + name + '/' + first_id + '/' + second_id + '/Web01/en/summary.html'
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
            parts = (
                self.parsed_url.scheme,
                self.parsed_url.netloc,
                newpath,
                self.parsed_url.query,
                self.parsed_url.fragment,
            )
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
        return 'https://results.enr.clarityelections.com/' + self.state

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
        except (IndexError, AttributeError):
            segment = tree.xpath("//script")[0].values()[0].split('/')[1]
        return '/' + segment + '/en/summary.html'

    def report_url(self, fmt):
        """
        Returns link to detailed report depending on format. Formats are xls, txt and xml.
        """
        url = self._state_url() + '/' + '/'.join(self.parsed_url.path.split('/')[2:-2]) + "/reports/detail{}.zip".format(fmt)
        r = requests.get(url, headers={"User-Agent": "Mozilla/5.0 (platform; rv:geckoversion) Gecko/geckotrail Firefox/firefoxversion"})
        if r.status_code == 200:
            return url
        else:
            return None

    def _get_summary_url(self):
        """
        Returns the summary report URL for a jurisdiction.
        """
        url = self._state_url() + '/' + '/'.join(self.parsed_url.path.split('/')[2:-2]) + "/reports/summary.zip"
        r = requests.get(url, headers={"User-Agent": "Mozilla/5.0 (platform; rv:geckoversion) Gecko/geckotrail Firefox/firefoxversion"})
        if r.status_code == 200:
            return url
        else:
            return None
