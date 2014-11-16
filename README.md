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

Clarify's `Parser` class accepts a file or file-like object representing the unzipped election results file in XML format and parses it into Python objects containing details about specific elections (which are called contests in the schema) and results. Clarify's parser accepts a file or file-like object, which means that the user needs to handle the downloading and un-zipping portion of the workflow:

```
>>> p = clarify.Parser()
>>> p.parse("path/to/detail.xml")
>>> p.election_name
'2012 General Election'
>>> p.region
'Arkansas'
>>> p.contests
[Contest(key='0103', text='U.S. President and Vice President', vote_for=1, is_question=False, precincts_reporting=30, precincts_participating=None, precincts_reported=30, counties_participating=None, counties_reported=None), Contest(key='0104', text='U.S. Congress District 1', vote_for=1, is_question=False, precincts_reporting=30, precincts_participating=None, precincts_reported=30, counties_participating=None, counties_reported=None)...]
```

`Parser` instances have convenience methods to list all contests, result jurisdictions and results. `Parser` objects provide access to both summary and detailed data about contests, including the vote 'choices' which can represent candidates or Yes/No types of questions. A sample result showing Election Day votes for Barack Obama in the 2012 presidential election in the LaGrue precinct in Arkansas County, Arkansas:

```
>>> p.contests[0].results[450]
Result(contest=Contest(key='0103', text='U.S. President and Vice President', vote_for=1, is_question=False, precincts_reporting=30, precincts_participating=None, precincts_reported=30, counties_participating=None, counties_reported=None), vote_type='Election Day', jurisdiction=ResultJurisdiction(name='LaGrue', total_voters=531, ballots_cast=381, voter_turnout=71.75, percent_reporting=4.0, precincts_participating=None, precincts_reported=None, precincts_reporting_percent=None, level='precinct'), votes=32, choice=Choice(contest=Contest(key='0103', text='U.S. President and Vice President', vote_for=1, is_question=False, precincts_reporting=30, precincts_participating=None, precincts_reported=30, counties_participating=None, counties_reported=None), key='004', text='Barack Obama / Joe Biden', total_votes='2455'))
```

A single `Result` object includes summary level information about the `ResultJurisdiction` (the precinct here), the contest and the choice for the jurisdiction containing the result (in this case, Arkansas County). Clarify's object models attempt to match the original XML schema as closely as possible.

Running tests
-------------

```
python setup.py test
```

Right now, the tests take about a minute to run, mostly because of the large number of http requests involved in the process. Speeding up that portion of the code is a goal.

Issues
------

To report an bug or request a feature, please [create a new issue](https://github.com/openelections/clarify/issues) describing the situation, providing as much detail as possible. Bear in mind that we are using Clarify to load election results data as part of OpenElections and thus supporting states that use it likely will be the highest priority. We welcome contributions: feel free to fork the code and submit pull requests.

License
-------

Clarify is released under the MIT License.
