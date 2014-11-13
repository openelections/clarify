import urlparse

import requests
import lxml.html
from lxml.cssselect import CSSSelector


class Jurisdiction(object):
    """
    Returns an object representing a state, county or city that has
    a Clarity election results page, and methods for retrieving
    additional information about those results.
    """

    def __init__(self, url, level):
        """
        Should we check that url contains "http://results.enr.clarityelections.com/"?
        Should we check that level is one of ('state','county','city')?
        """

        self.url = url
        self.level = level


    def get_sub_jurisdictions(self):
        """
        Returns an array of sub-jurisdictions depending on the level
        of the main jurisdiction. States always have counties, and
        counties and cities may have precincts.
        """

        # load url
        # parse counties if state

        county_url = get_county_url()
        r = requests.get(county_url)
        r.raise_for_status()
        return [(self._clarity_county_url(path), county) for path, county
                in self._scrape_county_paths(r.text)]

    def get_county_url(self):
        parsed = urlparse.urlsplit(self.url)
        newpath = '/'.join(parsed.path.split('/')[:-1]) + '/select-county.html'
        parts = (parsed.scheme, parsed.netloc, newpath, parsed.query,
                 parsed.fragment)
        return urlparse.urlunsplit(parts)

    def _clarity_county_url(self, path):
        url = self._clarity_election_base_url(self.CLARITY_PORTAL_URL +
            path.lstrip('/'))
        r = requests.get(url)
        r.raise_for_status()
        redirect_path = self._scrape_county_redirect_path(r.text)
        return url + redirect_path

    def detail_xml_url(self):
        """
        Returns a url to a zip file containing detailed results
        data in XML.
        """

        pass
