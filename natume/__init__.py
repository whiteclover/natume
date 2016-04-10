#!/usr/bin/env python
# Copyright (C) 2015 Thomas Huang
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 2 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


__version__ = '0.1.0'


from natume.client import WebClient
from natume.parser import DSLParser
from natume.testcase import WebTestCase, DSLWebTestCase


__all__ = [
    'WebClient',
    'DSLParser',
    'WebClient',
    'WebTestCase',
    'DSLWebTestCase',
    'Natume']


import unittest
import os
import os.path


class Natume(object):

    def __init__(self, url=None, paths=None, debug=None):
        self.paths = paths
        self.url = url
        self.debug = debug

    def default_namespace(self):
        client = WebClient(self.url)
        return {
            'client': client,
            'WebTestCase': WebTestCase
        }

    def run(self):
        test_classes_to_run = []
        for path in self.paths:
            if os.path.isdir(path):
                for root, dirs, files in os.walk(path):
                    for f in files:
                        test_class = self.gen_test_class_from_file(path, f)
                        if test_class:
                            test_classes_to_run.append(test_class)
            else:
                path, filename = os.path.split(path)
                test_class = self.gen_test_class_from_file(path, filename)
                if test_class:
                    test_classes_to_run.append(test_class)

        loader = unittest.TestLoader()

        suites_list = []
        for test_class in test_classes_to_run:
            suite = loader.loadTestsFromTestCase(test_class)
            suites_list.append(suite)

        big_suite = unittest.TestSuite(suites_list)
        verbosity = 2 if self.debug else 0
        runner = unittest.TextTestRunner(verbosity=verbosity)
        results = runner.run(big_suite)
        return results

    def gen_test_class_from_file(self, path, filename):
            name, ext = filename.split('.')
            if ext == 'smoke':
                code, class_name = self.gen_testcase(path, filename)
                ns = self.default_namespace()
                exec code in ns
                return ns[class_name]

    def gen_testcase(self, path, filename):
        dsl_parser = DSLParser()
        dsl_parser.parse(path, filename)
        dsl_parser.complie()
        return dsl_parser.code, dsl_parser.class_name

