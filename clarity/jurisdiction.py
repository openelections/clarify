import six
from six.moves.urllib import parse

import requests
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
        Should we check that url contains "http://results.enr.clarityelections.com/"?
        Should we check that level is one of ('state','county','city')?
        """

        self.url = url # always a summary.html
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
            return []
        try:
            r = requests.get(subjurisdictions_url)
            r.raise_for_status()
            results = [(self._clarity_subjurisdiction_url(path), subjurisdiction) for path, subjurisdiction
                    in self._scrape_subjurisdiction_paths(r.text)]
            return [Jurisdiction(url, 'county', name) for url, name in results]
        except requests.exceptions.HTTPError:
            return []

    def _parse_url(self):
        return parse.urlsplit(self.url)

    def _get_state_from_url(self):
        return self.parsed_url.path.split('/')[1]

    def _get_subjurisdictions_url(self):
        if self.level != 'state':
            return None
        else:
            newpath = '/'.join(self.parsed_url.path.split('/')[:-1]) + '/select-county.html'
            parts = (self.parsed_url.scheme, self.parsed_url.netloc, newpath, self.parsed_url.query,
                     self.parsed_url.fragment)
            return parse.urlunsplit(parts)

    def _scrape_subjurisdiction_paths(self, html):
        tree = lxml.html.fromstring(html)
        sel = CSSSelector('ul li a')
        results = sel(tree)
        return [(match.get('value'), match.get('id')) for match in results]

    def _clarity_subjurisdiction_url(self, path):
        url = self._clarity_state_url() + "/".join(path.split('/')[:3])
        r = requests.get(url)
        r.raise_for_status()
        redirect_path = self._scrape_subjurisdiction_summary_path(r.text)
        return url + redirect_path

    def _clarity_state_url(self):
        return 'http://results.enr.clarityelections.com/' + self.state

    def _scrape_subjurisdiction_summary_path(self, html):
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
        return self._clarity_state_url() + '/' + '/'.join(self.parsed_url.path.split('/')[2:-2]) + "/reports/detail{}.zip".format(fmt)

    def _get_summary_url(self):
        return self._clarity_state_url() + '/' + '/'.join(self.parsed_url.path.split('/')[2:-2]) + "/reports/summary.zip"
