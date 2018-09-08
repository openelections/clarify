#!/usr/bin/env python

from setuptools import setup, find_packages

# PyPI only supports nicely-formatted README files in reStructuredText.
# GitHub and @dwillis prefer Markdown.  Use a version of the pattern from
# https://coderwall.com/p/qawuyq/use-markdown-readme-s-in-python-modules
# to convert the Markdown README to rst if the pypandoc package is
# present.
try:
    import pypandoc
    long_description = pypandoc.convert('README.md', 'rst')
except (IOError, ImportError, OSError):
    long_description = open('README.md').read()

# Load the version from the clarify.version module
exec(open('clarify/version.py').read())

setup(
    name='Clarify',
    version=__version__,
    author='OpenElections',
    author_email='openelections@gmail.com',
    url='http://openelections.net',
    description=('A library for scraping and parsing election results from '
                 'jurisdictions using Clarity elections systems.'),
    long_description=long_description,
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'requests',
        'lxml',
        'cssselect',
        'six',
        'python-dateutil',
        'requests-futures',
    ],
    tests_require=[
        'nose',
        'responses',
        "unittest2; python_version < '3.4'"
    ],
    test_suite='nose.collector',
    keywords=['elections', 'Clarity', 'results', 'parser', 'scraper'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Topic :: Internet',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Text Processing',
        'Topic :: Text Processing :: Markup :: XML',
    ],
)
