# Development
This is a short summary about how to configure the development environment.

## Python environment
This project is using `uv` for Python project management, see more details about [installation of `uv`](https://docs.astral.sh/uv/getting-started/installation/).
`uv` can provide everything that multiple tools (e.g. `pip`, `pyenv`, `venv`) provide, but much faster. For example:

* install a Python run-time: `uv python install 3.14`
* use a specific Python version: `uv python pin 3.14`
* create virtual Python environment: `uv venv`
* install all dependencies: `uv sync`
* build package: `uv build`

`uv` has a lock file (`uv.lock`) storing all dependencies, this should be part of version control.

Building a development environment from scratch (with Python 3.14) contains the following steps:
```
      pipx install uv
      pipx ensurepath
      git clone https://github.com/petersulyok/diskinfo.git
      cd diskinfo
      uv python install 3.14
      uv python pin 3.14
      uv sync
```
`uv sync` also installs the `diskinfo` package itself in editable mode, so no extra installation step is needed.
The tools can be executed with `uv run` without activating the virtual environment.
Dependencies are listed in `pyproject.toml` file and the proper version numbers are handled by `uv`:
```
      dependencies = [
          "pySMART",
          "pyudev"
      ]
      
      [dependency-groups]
      dev = [
          "build",
          "coverage",
          "pytest",
          "pytest-cov",
          "twine"
      ]
      lint = [
          "ruff",
          "pylint"
      ]
      doc = [
          "alabaster",
          "Sphinx",
          "sphinx-rtd-theme",
          "sphinx-copybutton"
      ]
      demo = [
          "rich"
      ]
```
## Linting
The code can be checked with `pylint` and `ruff`:
```
   uv run pylint src/diskinfo/ test/
   uv run ruff check .
```
Their configuration options can be found in `pyproject.toml` file.
## Unit tests
The unit tests can be executed with `pytest`:
```
   uv run pytest
```
The coverage can be also measured for unit tests:
```
   uv run pytest --cov --cov-report=html
```
The HTML report will be generated at `./htmlcov` directory. The coverage settings are in `pyproject.toml` file,
100% coverage is required, otherwise the coverage measurement fails.


## PyPI package
The `setuptools` is used to create Python distribution package to PyPI. All package parameters are specified in 
`pyproject.toml` file. The package can be created in `dist` directory:
```
   uv build
```
The new package can be uploaded to PyPI with `twine`:
```
   uv run twine upload --verbose dist/*
```
NOTE: The distribution package will be built and published to PyPI automatically when a new GitHub release created!


## Documentation
This project is using `sphinx` to generate documentation on [readthedocs.io](https://readthedocs.io/). The
GitHub repository is connected to [readthedocs.io](https://readthedocs.io/) and when a new commit is
created in GitHub, it will trigger documentation update on  [readthedocs.io](https://readthedocs.io/) side.
The required Python packages are managed by `uv`. The documentation can be built and tested locally:
```
   cd docs
   uv run make html
```
The HTML documentation will be created in `./docs/build/html` folder.

NOTE: Many times the browsers do not display new version of documentation (because of caching). You may try to reload
the page ignoring browser cache (e.g. CTRL + SHIFT + R).


## GitHub workflows
The project implemented the following GitHub workflows:

1. **Unit test and lint execution** (`test.yml`). A commit triggers this action:
   - executes unit test on `ubuntu-latest` OS and on Python versions `3.11`, `3.12`, `3.13`, `3.14`, `3.15`
   - executes `pylint` and `ruff`
   - generates coverage data and upload it to [codecov.io](https://codecov.io/)

2. **Publish Python distribution packages to PyPI** (`publish.yml`). A published release triggers this action:
   - build distribution package on Python `3.14`
   - upload the new package to PyPI

## How to create a new release
Follow these steps to create a new release:

1. Commit all changes
2. Run `pytest`, `pylint` and `ruff` and correct all warnings and errors
3. Generate documentation locally and check it
4. Change the version number in `pyproject.toml`
5. Update `CHANGELOG.md` with the new release information
6. Update the version number in  `docs/source/conf.py` 
7. Commit all changes and test again
8. Create a new release on GitHub with the same version number and the new package will be published on PyPI
   automatically
