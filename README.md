=====================
Clarify
=====================

A Python library to discover and parse results for jurisdictions that use election results reporting systems from [SOE Software](http://www.soesoftware.com/product/clarity-election-night-reporting/), a Florida-based company that offers its products under the "Clarity" name. Web sites using Clarity are recognizable by URLs that begin with "http://results.enr.clarityelections.com" and have zip files containing structured data in XML, CSV and XLS format.

Clarify offers an interface for discovering the locations of those zip files and another for parsing the XML versions of the data contained within them. Currently it does not handle downloading and unzipping those files, leaving that to the user.

Clarify has been tested under Python 2.7.X and 3.4.1.

Installation
-------------

Until Clarify is published on PyPy, install from the GitHub repository:

```
pip install -e git://github.com/openelections/clarify.git#egg=clarify
```

Usage
-----

Election results sites running Clarity software offer detailed election results at the level of the political jurisdiction (for example, a state or county) and, optionally, sub-jurisdictions beneath that (counties and/or precincts). Clarify provides methods for discovering the URLs of structured data files and for parsing the XML versions of those files into Python objects.

*Jurisdiction*

Clarify's `Jurisdiction` class provides details about the jurisdiction represented by a Clarity URL and the data available from that jurisdiction. To create an instance, pass in a Clarity results URL and the level of the jurisdiction ('state', 'county', or 'city'). The object then provides access to the detailed XML results for that jurisdiction:

```
>>> import clarify
>>> j = clarify.Jurisdiction(url='http://results.enr.clarityelections.com/KY/15261/30235/en/summary.html', level='state')
>>> j.report_url('xml')
'http://results.enr.clarityelections.com/KY/15261/30235/reports/detailxml.zip'
```

The `Jurisdiction` object also provides access to any sub-jurisdiction details, including the URL of the detailed XML results, by scraping the web pages listing them:

```
>>> subs = j.get_subjurisdictions()
>>> subs[0].name
'Adair'
>>> subs[0].report_url('xml')
'http://results.enr.clarityelections.com/KY/Adair/15263/27401/reports/detailxml.zip'
```

*Parser*

Clarify's `Parser` class accepts a file or file-like object representing the unzipped election results file in XML format and parses it into Python objects.

Running tests
-------------

```
python setup.py test
```

Right now, the tests take about a minute to run, mostly because of the large number of http requests involved in the process. Speeding up that portion of the code is a goal.
