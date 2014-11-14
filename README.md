=====================
Clarify
=====================

A Python library to discover and parse results for jurisdictions that use election results reporting systems from [SOE Software](http://www.soesoftware.com/product/clarity-election-night-reporting/), a Florida-based company that offers its products under the "Clarity" name. Web sites using Clarity are recognizable by URLs that begin with "http://results.enr.clarityelections.com" and have zip files containing structured data in XML, CSV and XLS format.

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

To see this in action, 




Running tests
-------------

```
python setup.py test
```
