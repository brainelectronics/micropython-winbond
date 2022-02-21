# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

<!--
## [x.y.z] - yyyy-mm-dd
### Added
### Changed
### Removed
### Fixed
-->

## [0.2.0] - 2022-02-21
### Added
- [`setup.py`](setup.py) and [`sdist_upip.py`](sdist_upip.py) taken from
  [pfalcon's picoweb repo][ref-pfalcon-picoweb-sdist-upip] and PEP8 improved
- [`MIT License`](LICENSE)

### Changed
- Moved [`winbond.py`](winbond/winbond.py) into folder named `winbond`
- Update README usage description of micropython lib deploy to [PyPi][ref-pypi]
- Renamed `test_winbond.py` to [`usage_example.py`](usage_example.py)

## [0.1.0] - 2022-02-17
### Added
- This changelog file
- Default python [`.gitignore`](.gitignore) file
- MicroPython [`boot`](boot.py) and [`main`](main.py) files
- [`README`](README.md) and [`requirements.txt`](requirements.txt) files
- [`winbond.py`](winbond.py) file based on [crizeo's answer on the MicroPython
  Forum][ref-upy-forum-winbond-driver] with my extension to use flash chips
  without hardware reset pins, extended documentation and PEP8 fixes

<!-- Links -->
[Unreleased]: https://github.com/brainelectronics/micropython-winbond/compare/0.2.0...develop

[0.2.0]: https://github.com/brainelectronics/micropython-winbond/tree/0.2.0
[0.1.0]: https://github.com/brainelectronics/micropython-winbond/tree/0.1.0
[ref-upy-forum-winbond-driver]: https://forum.micropython.org/viewtopic.php?f=16&t=3899&start=10
[ref-pypi]: https://pypi.org/
[ref-pfalcon-picoweb-sdist-upip]: https://github.com/pfalcon/picoweb/blob/b74428ebdde97ed1795338c13a3bdf05d71366a0/sdist_upip.py
