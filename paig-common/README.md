# shield-common


## Development
```
# go inside the project repository
cd shield-common

# setup environment
python3  -m venv venv

# activate environment
. venv/bin/activate

# install dependencies
pip install -r requirements.txt

```

## Tests
```
# go to shield directory inside the project repository
cd shield-common

# activate environment
. venv/bin/activate

# run tests with coverage
echo -e "[run]\nomit = tests/*, **/__init__.py" > .coveragerc
python3 -m pytest --cov=. --cov-report term:skip-covered --cov-report html:coverage_reports tests --disable-warnings

```