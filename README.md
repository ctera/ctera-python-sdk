# CTERA for Python
[![Build Status](https://travis-ci.com/CTERA-Networks/ctera-python-sdk.svg?branch=master)](https://travis-ci.com/CTERA-Networks/ctera-python-sdk)
[![Documentation Status](https://readthedocs.org/projects/ctera-python-sdk/badge/?version=latest)](https://ctera-python-sdk.readthedocs.io/en/latest/?badge=latest)

## Installing
Installing via pip

```bash
   pip install cterasdk-3.1.zip
```
If you don't have `pip` installed, you may use the following alternative:

```bash
   python setup.py install
```
## Importing the Library

```python
from cterasdk import *
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
