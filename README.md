Clarify
=======

[![Build Status](https://travis-ci.org/openelections/clarify.svg?branch=master)](https://travis-ci.org/openelections/clarify)
[![Code Coverage](https://codecov.io/gh/openelections/clarify/branch/master/graph/badge.svg)](https://codecov.io/gh/openelections/clarify)

A Python library to discover and parse results for jurisdictions that use election results reporting systems from [SOE Software](http://www.soesoftware.com/product/clarity-election-night-reporting/), a Florida-based company that offers its products under the "Clarity" name. Web sites using Clarity are recognizable by URLs that begin with "http://results.enr.clarityelections.com" and have zip files containing structured data in XML, CSV and XLS format.

Clarify offers an interface for discovering the locations of those zip files and another for parsing the XML versions of the data contained within them. Currently it does not handle downloading and unzipping those files, leaving that to the user.

Clarify is tested using Python 2.7, 3.4, 3.5, and 3.6.

Installation
-------------

Clarify can be installed using pip:

```
pip install clarify
```

Usage
-----

Election results sites running Clarity software offer detailed election results at the level of the political jurisdiction (for example, a state or county) and, optionally, sub-jurisdictions beneath that (counties and/or precincts). Clarify provides methods for discovering the URLs of structured data files and for parsing the XML versions of those files into Python objects.

### Jurisdiction

Clarify's `Jurisdiction` class provides details about the jurisdiction represented by a Clarity URL and the data available from that jurisdiction. To create an instance, pass in a Clarity results URL and the level of the jurisdiction ('state', 'county', or 'city'). The object then provides access to the detailed XML results for that jurisdiction:

```
>>> import clarify
>>> j = clarify.Jurisdiction(url='http://results.enr.clarityelections.com/GA/63991/184321/en/summary.html', level='state')
>>> j.report_url('xml')
'https://results.enr.clarityelections.com/GA/63991/184321/reports/detailxml.zip'
```

The `Jurisdiction` object also provides access to any sub-jurisdiction details, including the URL of the detailed XML results, by scraping the web pages listing them:

```
>>> subs = j.get_subjurisdictions()
>>> subs[0].name
'Baldwin'
>>> subs[0].report_url('xml')
'https://results.enr.clarityelections.com/GA/Baldwin/63997/183266/reports/detailxml.zip'
```

### Parser

Clarify's `Parser` class accepts a file or file-like object representing the unzipped election results file in XML format and parses it into Python objects containing details about specific elections (which are called contests in the schema) and results.  The parser only handles the parsing of the XML into objects which make the election data easy to access.  the user needs to handle the downloading and un-zipping portion of the workflow.

Create a new parser object and parser a results XML file:

```
>>> p = clarify.Parser()
>>> p.parse("path/to/detail.xml")
```

Once the ``parse()`` method has been called, the `Parser` object has properties that provide information about the election and jurisdiction of the results file:

```
>>> p.election_name
'2012 General Election'
>>> p.region
'Arkansas'
```

The parser object also has properties that provide lists of all contests, result jurisdictions and results.

A list of all contests:


```
>>> p.contests
[Contest(key='0103', text='U.S. President and Vice President', vote_for=1, is_question=False, precincts_reporting=30, precincts_participating=None, precincts_reported=30, counties_participating=None, counties_reported=None), Contest(key='0104', text='U.S. Congress District 1', vote_for=1, is_question=False, precincts_reporting=30, precincts_participating=None, precincts_reported=30, counties_participating=None, counties_reported=None)...]
```

A list of all sub-jurisdictions that have results:

```
>>> p.result_jurisdictions
[ResultJurisdiction(name='Gillett Ward 1', total_voters=121, ballots_cast=74, voter_turnout=61.16, percent_reporting=4.0, precincts_participating=None, precincts_reported=None, precincts_reporting_percent=None, level='precinct'), ResultJurisdiction(name='Gillett Ward 2', total_voters=139, ballots_cast=111, voter_turnout=79.86, percent_reporting=4.0, precincts_participating=None, precincts_reported=None, precincts_reporting_percent=None, level='precinct'),...]
```

A list of all results, from all contests, from all sub-jurisdictions.  This is useful if you want to transform all the results into another format:

```
>>> p.results[0:3]
[Result(contest=Contest(key='0103', text='U.S. President and Vice President', vote_for=1, is_question=False, precincts_reporting=30, precincts_participating=None, precincts_reported=30, counties_participating=None, counties_reported=None), vote_type='overVotes', jurisdiction=None, votes=0, choice=None), Result(contest=Contest(key='0103', text='U.S. President and Vice President', vote_for=1, is_question=False, precincts_reporting=30, precincts_participating=None, precincts_reported=30, counties_participating=None, counties_reported=None), vote_type='overVotes', jurisdiction=ResultJurisdiction(name='Gillett Ward 1', total_voters=121, ballots_cast=74, voter_turnout=61.16, percent_reporting=4.0, precincts_participating=None, precincts_reported=None, precincts_reporting_percent=None, level='precinct'), votes=0, choice=None), Result(contest=Contest(key='0103', text='U.S. President and Vice President', vote_for=1, is_question=False, precincts_reporting=30, precincts_participating=None, precincts_reported=30, counties_participating=None, counties_reported=None), vote_type='overVotes', jurisdiction=ResultJurisdiction(name='Gillett Ward 2', total_voters=139, ballots_cast=111, voter_turnout=79.86, percent_reporting=4.0, precincts_participating=None, precincts_reported=None, precincts_reporting_percent=None, level='precinct'), votes=0, choice=None)]
```

`Parser` objects also have convenience methods for retrieving specific contests (`get_contest()`) and jurisdictions (`get_result_jurisdiction()`).

Get a `Contest` object for the presidential contest:

```
>>> contest = p.get_contest("U.S. President and Vice President")
>>> contest
Contest(key='0103', text='U.S. President and Vice President', vote_for=1, is_question=False, precincts_reporting=30, precincts_participating=None, precincts_reported=30, counties_participating=None, counties_reported=None)
```

`Contest` objects provide access to both summary and detailed data about contests, including the vote 'choices' which can represent candidates or Yes/No types of questions.

```
>>> for c in contest.choices:
...     print(c.text)
...
Gary Johnson / James P. Gray
Jill Stein / Cheri Honkala
Mitt Romney / Paul Ryan
Barack Obama / Joe Biden
Peta Lindsay / Yari Osorio
```

`Contest` objects also provide access to all the ``Result`` objects for the contest. A single `Result` object includes summary level information about the `ResultJurisdiction` (the precinct here), the contest and the choice. Clarify's object models attempt to match the original XML schema as closely as possible.

Get a single result for the contest:

```
>>> result = contest.results[450]
>>> result
Result(contest=Contest(key='0103', text='U.S. President and Vice President', vote_for=1, is_question=False, precincts_reporting=30, precincts_participating=None, precincts_reported=30, counties_participating=None, counties_reported=None), vote_type='Election Day', jurisdiction=ResultJurisdiction(name='LaGrue', total_voters=531, ballots_cast=381, voter_turnout=71.75, percent_reporting=4.0, precincts_participating=None, precincts_reported=None, precincts_reporting_percent=None, level='precinct'), votes=32, choice=Choice(contest=Contest(key='0103', text='U.S. President and Vice President', vote_for=1, is_question=False, precincts_reporting=30, precincts_participating=None, precincts_reported=30, counties_participating=None, counties_reported=None), key='004', text='Barack Obama / Joe Biden', total_votes='2455'))
```

This result shows election day votes for Barack Obama in the 2012 presidential election in the LaGrue precinct in Arkansas County, Arkansas.  These pieces of information are available as properties of the `Result` object.

Get the candidate name for the result:

```
>>> result.choice.text
'Barack Obama / Joe Biden'
```

Get the type of votes for this result:

```
>>> result.vote_type
'Election Day'
```

Get the name of the jurisdiction of this result:

```
>>> result.jurisdiction.name
'LaGrue'
```

Get the number of votes:

```
>>> result.votes
32
```

Running tests
-------------

```
python setup.py test
```

Issues
------

To report an bug or request a feature, please [create a new issue](https://github.com/openelections/clarify/issues) describing the situation, providing as much detail as possible. Bear in mind that we are using Clarify to load election results data as part of OpenElections and thus supporting states that use it likely will be the highest priority. We welcome contributions: feel free to fork the code and submit pull requests.

License
-------

Clarify is released under the MIT License.
