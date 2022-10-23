# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).


## [2.0.0] - 2022-10-23

### Added
- New `Partition` class added to hold partition data
- `get_partition_list()` method of `Disk` class returns the list of partitions
- New utility functions are available,`size_in_hrf()` and `time_in_hrf()`, to display size and time in human-readable
  form
- Demo has been extended with two additional screens (disk attributes, partition data)
- Documentation has been improved and updated for the new functionality
- Unit tests has been extended to cover the new functionality

### Changed
- Demo cannot be executed without [`rich`](https://pypi.org/project/rich/) Python library


## [1.3.1] - 2022-10-06

### Fixed
- `pytest` coverage measurement and upload to codecov fixed


## [1.3.0] - 2022-10-06

### Added
- Documentation extended with examples for all functions.
- `pyproject.toml` configuration file used for all tools

## [1.2.0] - 2022-10-02

### Added
- A new method, called `get_smart_data()`, has been implemented in `Disk` class. It returns the SMART data of the
  disk (feature request in issue #3 implemented). Additional classes have been defined for SMART data:
  `DiskSmartData()`, `SmartAttribute()`, `NvmeAttributes()`.
- Documentation, unit tests have been updated
### Removed
- Python 3.6 has been removed from list of the supported Python versions because the package building and isnallation
  is not working here.

## [1.1.0] - 2022-09-25

### Added
- A new method, called `get_temperature()`, has been implemented in `Disk` class. It returns the temperature of the
  disk (feature request in issue #2 implemented).
- Documentation, unit tests have been updated

## [1.0.1] - 2022-09-24

### Fixed
- PyPI package version number fixed

## [1.0.0] - 2022-09-24
First official release

### Added
- Planned functionality implemented
- Unit tests are implemented, coverage is 100%, connected to [codecov.io](https://codecov.io)
- The code is linted with `flake8` and `pylint` 
- API documentation is created and published on [readthedocs.io](https://readthedocs.io)
- Python distribution package is published on PyPI
- Github workflows are implemented to automate testing and package publishing
