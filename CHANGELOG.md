# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [3.2.0] - 2026-02-20

### Added
- Python 3.14 support added
- Project switched to `uv` for Python project management
- Disk management uses `pyudev` python module
- Unit tests refactored in pytest style.
- GitHub workflows updated to `uv`.


## [3.1.2] - 2024-04-13

### Fixed
- GitHub actions updated to the latest version in worflow file, a new token is created for codecov.


## [3.1.1] - 2024-04-06

### Fixed
- Issue #6 : exception raised if partition information is missing for an USB HDD


## [3.1.0] - 2024-03-10

### Added
- A new encoding parameter has been added to Disk.__init__() and file utility methods to let user specify the proper
  encoding for file and string operations.

### Fixed
- Encoding and parsing issues in partition data have been fixed (reported in issue #5):
   - Partition mounting point containing space character was displayed improperly in the demo
   - Partition label containing non-ascii character was displayed improperly in the demo
- The demo won't stop if a disk does not have temperature (e.g. USB pendrive) 


## [3.0.0] - 2024-03-03

### Added
- [pySMART](https://pypi.org/project/pySMART/) library used in the refactored `Disk.get_temperature()` and
  `Disk.get_smart_data()` methods
- New attributed added for `NvmeAttributes()` class
- New attributed added for `DiskSmartData()` class

### Changed
- support of Python 3.7 removed

### Fixed
- LOOP disks handled without problems
- `Disk.get_smart_data()` can be executed on a wider range of hard disks and SSDs without problems


## [2.1.2] - 2024-01-02

### Added
- New chapter for explaining the use of `create_python_env.sh`

### Fixed
- `create_python_env.sh`: better error handling for non-exiting Python version


## [2.1.1] - 2024-01-01

### Changed
- Copyright updated. 

### Fixed
- New version number is required for new PyPI release (release 2.1.0 was deleted on PyPI)


## [2.1.0] - 2024-01-01

### Added
- Support for Python 3.11 and 3.12
- A [new bash script](https://github.com/petersulyok/diskinfo/blob/main/bin/create_python_env.sh) added to create a virtual Python environment and install all dependencies.
- Documentation is updated

### Changed
- Dependency management: requirement files for `pip` are using maximal version numbers 
- Flake8 removed

### Fixed
- In case of loop disks, `Disk.get_temperature()` method did not work and the demo stopped. Better error handling added while loop devices will be fully supported.


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
