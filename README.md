# Installing
## Using PIP
The `ctera-python-sdk` package can be installed using the python package installer `pip`

```bash
   pip install cterasdk-3.1.zip
```
## Alternatives
If you don't have `pip` installed, you may use the following alternative:

```bash
   python setup.py install
```

# Building

## Dockerized build using [skipper](https://github.com/Stratoscale/skipper)

Use strato-skipper to isolate the build environment from your working machine

> Currently skipper is supported only for Linux

### Prerequisites

#### Install skipper
```bash
sudo pip install strato-skipper
```
### Run tests and build the package
```bash
skipper make
```
## Build directly on your working environment
Create a source distribution

```bash
python -B setup.py sdist --formats=tar,gztar,zip
```
