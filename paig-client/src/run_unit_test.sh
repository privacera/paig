#!/bin/bash

# NOTE- you should run the mock service in a separate terminal before running these tests
# clone the plugin-tests repo and run the mock service
# cd ../plugin-tests/mock-shield-service
# ./run.sh

#set -x
#if [ "$1" == "--with-reports" ]; then
  rm -rf coverage_report
#  COV_OPTIONS="--cov --cov-report=html:coverage_report --log-cli-level DEBUG --html=pytest_report.html --self-contained-html"

#else
#  COV_OPTIONS=""
#fi

COV_OPTIONS="--cov --cov-report=html:coverage_report --html=pytest_report.html --self-contained-html"

#pytest ${COV_OPTIONS} plugin/tests -m 'e2e_test or not e2e_test or interceptor_test or not interceptor_test'

python -m pytest ${COV_OPTIONS} tests

# e2e_tests - run these if you have a dummy service running to test against
#pytest ${COV_OPTIONS} plugin/tests/test_backend.py -m 'e2e_test or not e2e_test'
#pytest ${COV_OPTIONS} plugin/tests/test_client.py -m 'e2e_test or not e2e_test'
#pytest ${COV_OPTIONS} plugin/tests -m 'e2e_test' -k test_b_langchain_set_baseopenai_interceptor

# interceptor_tests - run these separately otherwise they fail - TODO: need to find why
#pytest ${COV_OPTIONS} plugin/tests/test_langchain_interceptors.py -m 'interceptor_test or not interceptor_test'