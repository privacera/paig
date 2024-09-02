# PAIG Shield Plugin Library 

## Development 
```
# setup environment
python3  -m venv venv
. venv/bin/activate
pip install -r requirements.txt

# install the plugin in editable form for development 
pip install -e plugin

# run tests
# First clone plugin-test repo and set up the environment
# https://gitlab.com/privacera/paig/plugin-test
# then run the mock-shield-service
# cd plugin-test/mock-shield-service
# ./run.sh
# The plugin_config.json and server_config.json are committed in Git
# But you can re-generate using gen_config.py in the mock-shield-service folder

pytest plugin/tests

pytest --cov --cov-report=html:coverage_re plugin/tests

pytest plugin/tests -k 'specific_test_name'

pytest -s --log-cli-level DEBUG plugin/tests -k 'specific test' | tee 1.out

# build local
./build.sh

# build.sh is used by CI as follows
./build.sh gitlab-plain
or 
./build.sh gitlab-pyarmor

# Before you commit, do the following 3 things -
 
# run flake8 and review and fix the findings 
flake8 plugin

# make sure the tests run successfully
# You need to start the mock-shield-service before running the tests
./run_tests.sh

# In pycharm, right click on src folder and select "Inspect Code"
# Go through all the warnings and errors and fix them 
```

