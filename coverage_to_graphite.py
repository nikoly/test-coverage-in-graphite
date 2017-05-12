#!/usr/bin/env python3


"""
It sends the unit tests coverage value to HostedGraphite.

The test coverage value is retrieved from a cobertura test coverage report.

Usage:

    export HOSTED_GRAPHITE_KEY = <api-key> // from Jenkins job environment
    export BRANCH_NAME = <git-branch-name> // from Jenkins job environment

    ./coverage_to_graphite.py <service-name> <path-to-report>
    
"""

from io import StringIO
import os
import sys
import logging
from lxml import etree
import requests


logger = logging.getLogger('send_coverage_to_graphite')
logging.basicConfig(level=logging.INFO)


class XMLFileHelper:

    def __init__(self, file_location):
        self.path = file_location

    def load(self):
        new_path = os.path.realpath(self.path)
        with open(new_path,'r') as file:
            return file.read()

    @classmethod
    def parse_xml(self, data):
        """ Parse XML file """
        # The data returned must be of type unicode
        # to make StringIO compatible with Python2.7
        return etree.parse(StringIO(u"""{}""".format(data)))

    @classmethod
    def fetch_coverage(self, tree):
        """ Returns value of unit test coverage as an integer value."""
        coverage = tree.xpath("number(/coverage/@line-rate)")

        if (type(coverage) == float) & (0.0 <= coverage <= 1.0):
            return int(coverage * 100)
        else:
            raise TypeError("The coverage value is not of type float. Value is: {}".format(coverage))

    def coverage(self):
        tree = self.parse_xml(self.load())
        return self.fetch_coverage(tree)


class GraphiteHelper:

    def __init__(self, api_key):
        self.graphite_url = "https://www.hostedgraphite.com/api/v1/sink"
        self.api_key = api_key

    @classmethod
    def build_metric(self, service, branch, coverage):
        """Example: test.coverage.device-metadata-service.master 32"""
        return "test.coverage.{}.{} {}".format(service, branch, coverage) 

    def post_metric(self, metric):
        """Send the metric to hosted graphite"""
        logger.info("Sending this metric: %s", metric)

        resp = requests.post(
            url=self.graphite_url,
            auth=(self.api_key, ""),
            data=metric
        )

        if resp.status_code != 202:
            raise RuntimeError("Response is: {}, {}.".format(resp.status_code, resp.content))
        else:
            logger.info("The metric %s is sent", metric)

    def send(self, service, branch, coverage):
        metric = self.build_metric(service, branch, coverage)
        self.post_metric(metric)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        logger.info("The script requires 2 arguments: service name and a coverage report location.")
    else:
        SERVICE = sys.argv[1]
        REPORT_LOCATION = sys.argv[2]
        API_KEY = os.environ.get('HOSTED_GRAPHITE_KEY')
        BRANCH = os.environ.get('BRANCH_NAME')

        coverage = XMLFileHelper(REPORT_LOCATION).coverage()
        GraphiteHelper(API_KEY).send(SERVICE, BRANCH, coverage)
