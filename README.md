# `miguel`

`miguel` is a command-line REPL for interfacing with the `magellan` framework.
It can be used to view progress of jobs and tasks in addition to issuing any commands supported by the magellan API.


## Setup

```bash
# Creating a virtualenv is recommended, especially for development
mkvirtualenv miguel
# Install requirements inside a venv (or not) as desired
pip install -r requirements.txt
```

## Usage

```bash
./miguel.py -b http://10.8.0.4:4567

./miguel.py --help
```
