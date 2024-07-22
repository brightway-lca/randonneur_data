# randonneur_data

[![PyPI](https://img.shields.io/pypi/v/randonneur_data.svg)][pypi status]
[![Status](https://img.shields.io/pypi/status/randonneur_data.svg)][pypi status]
[![Python Version](https://img.shields.io/pypi/pyversions/randonneur_data)][pypi status]
[![License](https://img.shields.io/pypi/l/randonneur_data)][license]

[![Read the documentation at https://randonneur_data.readthedocs.io/](https://img.shields.io/readthedocs/randonneur_data/latest.svg?label=Read%20the%20Docs)][read the docs]
[![Tests](https://github.com/brightway-lca/randonneur_data/actions/workflows/python-test.yml/badge.svg)][tests]
[![Codecov](https://codecov.io/gh/brightway-lca/randonneur_data/branch/main/graph/badge.svg)][codecov]

[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)][pre-commit]
[![Black](https://img.shields.io/badge/code%20style-black-000000.svg)][black]

[pypi status]: https://pypi.org/project/randonneur_data/
[read the docs]: https://randonneur_data.readthedocs.io/
[tests]: https://github.com/brightway-lca/randonneur_data/actions?workflow=Tests
[codecov]: https://app.codecov.io/gh/brightway-lca/randonneur_data
[pre-commit]: https://github.com/pre-commit/pre-commit
[black]: https://github.com/psf/black

## Installation

You can install _randonneur_data_ via [pip] from [PyPI]:

```console
$ pip install randonneur_data
```

## Contributing

Contributions are very welcome.
To learn more, see the [Contributor Guide][Contributor Guide].

## License

Distributed under the terms of the [MIT license][License],
_randonneur_data_ is free and open source software.

## Issues

If you encounter any problems,
please [file an issue][Issue Tracker] along with a detailed description.


<!-- github-only -->

[command-line reference]: https://randonneur_data.readthedocs.io/en/latest/usage.html
[License]: https://github.com/brightway-lca/randonneur_data/blob/main/LICENSE
[Contributor Guide]: https://github.com/brightway-lca/randonneur_data/blob/main/CONTRIBUTING.md
[Issue Tracker]: https://github.com/brightway-lca/randonneur_data/issues


## Building the Documentation

You can build the documentation locally by installing the documentation Conda environment:

```bash
conda env create -f docs/environment.yml
```

activating the environment

```bash
conda activate sphinx_randonneur_data
```

and [running the build command](https://www.sphinx-doc.org/en/master/man/sphinx-build.html#sphinx-build):

```bash
sphinx-build docs _build/html --builder=html --jobs=auto --write-all; open _build/html/index.html
```