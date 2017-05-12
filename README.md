# test-coverage-in-graphite

A Python script that parses a Cobertura test coverage report, creates a metric with a value and sends it to HostedGraphite.

Compatible with Python2.7 and Python3

# Usage

To install all the necessary libraries that are used in the script     

```pip install requirements.txt```

If there is no HOSTED_GRAPHITE_KEY or BRANCH_NAME in the environment, do

```export HOSTED_GRAPHITE_KEY = <api-key> ```
```export BRANCH_NAME = <git-branch-name> ```

Run the script

```./coverage_to_graphite.py <service-name> <path-to-report> ```

An use this metric to find your data:

```test.coverage.<service-name>.<branch-name>```
