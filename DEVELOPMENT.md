# Development Environment
This is short summary about how to setup the development environment

## Development tools

1. Install [`pyenv`](https://github.com/pyenv/pyenv) and install your preferred Python version
2. Install and activate virtual environment in your working directory

        python -m venv .venv
        source .venv/bin/activate

3. Update `pip` and install required Python tools defined in `requirements-dev.txt`:

        python -m pip install --upgrade pip
        pip install -r requirements-dev.txt

## Unit tests and linting
The unit tests can be executed with `pytest`:

    pytest

The coverage can be also measured for unit tests:

    pytest --cov=src --cov=test --cov-report=html

The HTML report will be generated at `./htmlcov` directory.
The package is checked with `flake8` and `pylint` as well. They can be executed manually:

    flake8
    pylint src/diskinfo/*.py test/*.py

Their configuration options can be found `pyproject.toml` file. 

## PyPI package
The `setuptools` is used to create Python distribution package to PyPI. All package parameters are specified in 
`pyproject.toml` file. The package can be created in `dist` directory:

    python -m build

The new package can be uploaded to PyPI with `twine`:

    twine upload --verbose dist/*

NOTE: The distribution package will be built and published to PyPI automatically when a new github release created!

During the development this package can be installed locally:

    pip install -e .


## Documentation
This project is using `sphinx` to generate documentation on [readthedocs.io](https://readthedocs.io/). The
github repository is connected to [readthedocs.io](https://readthedocs.io/) and when a new commit is
created in github, it will trigger documentation update on  [readthedocs.io](https://readthedocs.io/) side.

The documentation can be built and tested locally:

    cd docs
    pip install -r requirements.txt
    make html

The HTML documentation will be created in `./docs/build/html` folder.

NOTE: Many times the browsers do not display new version of documentation (because of caching?). You may try to reload
the page ignoring browser cache (e.g. CTRL + SHIFT + R).

## Github workflows
The project implemented the following github workflows:

1. **Unit test and lint execution** (`test.yml`). A commit triggers this action:
   - executes unit test on `ubuntu-latest` OS and on Python versions `3.7`, `3.8`, `3.9`, `3.10`, `3.11.0-rc.2`
   - executes `flake8` and `pylint`
   - generates coverage data and upload it to [codecov.io](https://codecov.io/)

2. **Publish Python distribution packages to PypI** (`publish.yml`). A published release triggers this action:
   - build distribution package on Python `3.10`
   - upload the new package to PyPI

## How to create a new release
Follow these steps to create a new release:

1. Commit all changes
2. Run `pytest`, `flake8`, `pylint` and correct all warnings and errors
3. Generate documentation locally and check it
4. Change the version number in `pyproject.toml`
5. Update `CHANGELOG.md` with the new release information
6. Update the version number in  `docs/source/conf.py` 
7. Commit all changes and test again
8. Create a new release on github with the same version number and the new package will be published on PyPI
   automatically
