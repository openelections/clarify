History
=======

0.7.0 (2025-05-24)
------------------

- **Python 3 Compatibility**: Full Python 3.8+ support with compatibility fixes
- **Dependency Updates**: Updated all dependencies to modern, secure versions
- **Bug Fixes**: 
  - Fixed bare exception handling in parser.py
  - Fixed dictionary `.values()` indexing for Python 3 compatibility
  - Fixed URL construction in jurisdiction.py
  - Fixed collections.Callable import for Python 3.10+
- **Build System**: Modernized to use pyproject.toml configuration
- **Testing**: Updated test framework from nose to pytest
- **Removed**: Python 2 compatibility code and deprecated dependencies

0.5.0 (2018-XX-XX)
------------------



0.4.0 (2018-10-06)
------------------

- Handle subjurisdiction without results (e.g. summary lines).
- Fix `#21 <https://github.com/openelections/clarify/issues/21>`_: url tests
  failing in test_jurisdiction (http / https issues)

  - Switch URLs to HTTPS.
  - Fix failing tests.

- Begin using continuous integration for build testing.
- Improve test coverage.
- Close `#16 <https://github.com/openelections/clarify/issues/16>`_: Add
  support for current_ver

  - Add support for determining the latest summary URL.

- Uplift missing changes from 0.1.2.
- Fix code formatting issues reported by flake8.

0.3.0 (2016-01-25)
------------------

- Add optional party attibute to Choice objects.

0.2.0 (2015-11-09)
------------------

- Fix `#14 <https://github.com/openelections/clarify/issues/14>`_: _parse_url
  not producing the correct report detail URLs

  - Add support for subjurisdictions that can only be found from /Web01/ URLs.
  - Add check to ensure report and summary URLs are valid.

- Add requirements.txt file.

0.1.2 (2014-11-30)
------------------

- Fix `#13 <https://github.com/openelections/clarify/issues/13>`_: Precinct
  lookup fails when precinct not in VoterTurnout element
- Refactor parser code.

0.1.1 (2014-11-25)
------------------

- Fix installation instructions.

0.1.0 (2014-11-25)
------------------

- Initial release.