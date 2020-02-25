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
