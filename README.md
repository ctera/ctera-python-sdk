# CTERA for Python
[![Build Status](https://travis-ci.com/CTERA-Networks/ctera-python-sdk.svg?branch=master)](https://travis-ci.com/CTERA-Networks/ctera-python-sdk)

## Installing
Installing via pip

```bash
   pip install cterasdk
```
If you don't have `pip` installed, you may use the following alternative:

```bash
   python setup.py install
```

## Building

### Prerequisites

#### Install tox
```bash
pip install tox
```

### Run all tests
Run all test environments
```bash
tox
```
You can also run specific tox environment, e.g:
```bash
tox -e lint
```

### Build directly on your working environment
Create a source distribution

```bash
python -B setup.py sdist --formats=tar,gztar,zip
```
