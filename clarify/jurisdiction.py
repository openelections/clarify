import concurrent.futures

from urllib import parse

import re
import requests
from requests_futures.sessions import FuturesSession
import lxml.html
from lxml.cssselect import CSSSelector

# base_uri is the path prefix including the folloing named groups:
# - state_id (required)
# - jurisdiction_name (optional) -- the city/county/precinct name, with URL-safe whitespace
# - election_id (required)
# - version number (optional)
# - additional path (optional)
BASE_URL_REGEX = re.compile(
    r'^'
    r'(?P<base_uri>.*)/'
    r'(?P<state_id>[A-Z]{2,2})'
    r'(?P<jurisdiction_name>/[A-Za-z_.]+)?'
    r'(?P<election_id>/[0-9]+)'
    r'(?P<version>/[0-9]+)?'
    r'(?P<path>.*)'
    r'$'
)
CLARITY_RESULTS_HOSTNAMES = ["results.enr.clarityelections.com", "www.enr-scvotes.org", "electionresults.iowa.gov"]
SUPPORTED_LEVELS = ['state', 'county', 'city', 'precinct']
UA_HEADER = {
    "User-Agent": "Mozilla/5.0 (platform; rv:geckoversion) Gecko/geckotrail Firefox/firefoxversion"
}


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
        if len([url for host in CLARITY_RESULTS_HOSTNAMES if(host in url)]) == 0:
            raise ValueError('Unsupported url origin')
        self.url = url
        self.parsed_url = self._parse_url(self.url)

        if type(level) != str:
            raise TypeError('Invalid level parameter')
        level = level.lower()
        if level not in SUPPORTED_LEVELS:
            raise ValueError('Unsupported level')
        self.level = level
        self.name = name
        self.summary_url = self._get_summary_url()

        if 'version' in self.parsed_url:
            self.current_ver = self.parsed_url['version']
        else:
            self.current_ver = self.get_current_ver(url)
            if self.current_ver:
                self.parsed_url['version'] = self.current_ver

    @classmethod
    def construct_url(cls, parsed_url, path, include_version=True):
        url_parts = []
        for key in ['base_uri', 'state_id', 'jurisdiction_name', 'election_id']:
            if key in parsed_url:
                url_parts.append(parsed_url[key])
        if include_version and 'version' in parsed_url:
            url_parts.append(parsed_url['version'])
        url_parts.append(path)
        return parse.urlunsplit(url_parts)

    @classmethod
    def get_current_ver(cls, election_url):
        parsed_url = cls._parse_url(election_url)
        # possible version filenames
        possible_filenames = ['current_ver.txt']
        ret = None
        for filename in possible_filenames:
            # if we have already seen a 200-status response
            if ret is None:
                current_ver_url = cls.construct_url(parsed_url, filename, include_version=False)
                current_ver_response = requests.get(current_ver_url, headers=UA_HEADER)
                try:
                    current_ver_response.raise_for_status()
                    ret = current_ver_response.text
                except requests.exceptions.HTTPError:
                    ret = None
        return ret

    @classmethod
    def get_latest_summary_url(cls, election_url):
        parsed_url = cls._parse_url(election_url)
        current_ver = cls.get_current_ver(election_url)

        # If we don't have current_ver, we can't determine a summary URL.
        if current_ver is None:
            return None
        parsed_url['version'] = current_ver

        new_paths = [
            "json/en/summary.json",
            "Web01/en/summary.html",
            "en/summary.html",
        ]

        for new_path in new_paths:
            latest_summary_url = cls.construct_url(parsed_url, new_path)

            latest_summary_url_response = requests.get(latest_summary_url, headers=UA_HEADER)

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
                r = requests.get(json_url, headers=UA_HEADER)
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
                r = requests.get(json_url, headers=UA_HEADER)
                r.raise_for_status()
                jurisdictions = []
                counties = r.json()['settings']['electiondetails']['participatingcounties']
                jurisdictions = self._get_subjurisdictions_urls_from_json(counties)
                return jurisdictions
            except requests.exceptions.HTTPError:
                json_url = self.url.replace('summary.html', 'json/en/electionsettings.json')
                try:
                    r = requests.get(json_url, headers=UA_HEADER)
                    r.raise_for_status()
                    jurisdictions = []
                    counties = r.json()['settings']['electiondetails']['participatingcounties']
                    jurisdictions = self._get_subjurisdictions_urls_from_json(counties)
                    return jurisdictions
                except requests.exceptions.HTTPError:
                    return []
        try:
            r = requests.get(subjurisdictions_url, headers=UA_HEADER)
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

    @classmethod
    def _parse_url(cls, url):
        """
        The parsed version of the original URL is used by several methods,
        so we assign it to self.parsed_url on init. If URL has "/Web01/"
        segment, that gets stripped out.
        """
        m = BASE_URL_REGEX.match(url)
        if not m:
            raise RuntimeError('Unable to parse ' + url)

        url_params = {}
        for k, v in m.groupdict().items():
            if not v:
                continue
            if v.startswith('/'):
                v = v[1:]
            url_params[k] = v
        return url_params

    def _get_subjurisdictions_urls_from_json(self, counties):
        subjurisdictions = []
        for c in counties:
            new_info = dict(self.parsed_url)
            new_info['jurisdiction_name'], new_info['election_id'], new_info['version'], date, fill = c.split('|')
            url = self.construct_url(new_info, 'Web01/en/summary.html')
            subjurisdictions.append(Jurisdiction(url, 'county', new_info['jurisdiction_name']))
        return subjurisdictions

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
            language = self.parsed_url['path'].split('/')[0]
            return self.construct_url(self.parsed_url, language + '/select-county.html')

    def _scrape_subjurisdiction_paths(self, html):
        """
        Parse subjurisdictions_url to find paths for counties.
        """
        tree = lxml.html.fromstring(html)
        sel = CSSSelector('ul li a')
        results = sel(tree)
        return [(match.get('value'), match.get('id')) for match in results]

    def _subjurisdiction_url_future(self, session, path):
        _, subjur_name, election_id, subpath = path.split('/')
        new_info = dict(self.parsed_url)
        new_info['jurisdiction_name'] = subjur_name

        # Make sure path ends with '/'
        # While the URL without the trailing forward slash will ultimately
        # resolve to the same place, it causes a redirect which means an
        # extra request.
        url = self.construct_url(new_info, '/', include_version=False)
        future = session.get(url)
        return future

    def _subjurisdiction_url_from_future(self, future):
        res = future.result()
        url = res.url
        redirect_path = self._scrape_subjurisdiction_summary_path(res.text)
        # We need to strip the trailing '/' from the URL before adding
        # the additional path
        return url.strip('/') + redirect_path

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

    def _get_report_url(self, fmt):
        """
        Return the url for the report in a given format without checking to see if it is valid.
        """
        return self.construct_url(self.parsed_url, "reports/detail{}.zip".format(fmt))

    def report_url(self, fmt):
        """
        Returns link to detailed report depending on format. Formats are xls, txt and xml.
        """
        url = self._get_report_url(fmt)
        r = requests.get(url, headers=UA_HEADER)
        if r.status_code == 200:
            return url
        else:
            return None

    def download_report(self, fmt, output_fn):
        """
        Downloads the selected report and saves it with the given output filename.
        """
        url = self._get_report_url(fmt)
        r = requests.get(url, headers=UA_HEADER)
        with open(output_fn, 'wb') as f:
            f.write(r.content)

    def _get_summary_url(self):
        """
        Returns the summary report URL for a jurisdiction.
        """
        url = self.construct_url(self.parsed_url, "reports/summary.zip")
        r = requests.get(url, headers=UA_HEADER)
        if r.status_code == 200:
            return url
        else:
            return None
