#!/usr/bin/env#!/usr/bin/env python
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


from natume.parser import DocDSLParser, CommandDslParser

from unittest import TestCase
import re


class WebTestCase(TestCase):
    """Web HTTP Test class

    handle json data
    handle http header

    """

    BODY_RE = re.compile('/(.*)/([ims]+)?')
    FLAGS = {
        'i': re.I,
        'm': re.M,
        's': re.S
    }

    def initialize(self):
        pass

    def assertHeader(self, key, value):
        """Check a head line value"""
        self.assertEqual(self.client.get_header(key), value)

    def assertContentType(self, value):
        """Check HTTP Response ContentType head"""
        self.assertEqual(self.client.content_type, value)

    def assertCharset(self, value):
        """Check HTTP Response charset info"""
        self.assertEqual(self.client.charset, value)

    def assertStatus(self, value):
        """Check HTTP Response Status code"""
        self.assertEqual(self.client.status, value)

    def assertCode(self, value):
        """Check HTTP Response Status code"""
        self.assertEqual(self.client.status_code, int(value))

    def assertContent(self, op, value):
        """Check HTTP Response Body"""
        self._assert_data(self.client.content, op, value)

    def assertJson(self, data, op, value):
        """Check Json/Restful api data"""
        self._assert_data(data, op, value)

    def _assert_data(self, data, op, value):

        if op == ':':
            # the key value equal assert
            self.assertEqual(data, value)

        elif op == '<-':
            # the key value in assert
            self.assertIn(value, data)

        elif op == '=~':
            # the key value regex match assert
            body_re = self._complie_body_re(value)
            self.assertTrue(body_re.search(data))

        elif op == '~~':
            # the key value length assert
            self.assertEqual(len(data), value)

    def _complie_body_re(self, value):
        m = self.BODY_RE.match(value)
        flag = None
        if m:
            body_re, flags = m.group(1), m.group(2)
            if flags:
                for _ in flags:
                    flag = flag | self.FLAGS[_] if flag else self.FLAGS[_]

        return re.compile(body_re, flag) if flag else re.compile(body_re)


def with_metaclass(meta, bases=(object,)):
    return meta("NewBase", bases, {})


def gen_test_methods_from_class(doc):
    doc_dsl = DocDSLParser()
    doc_dsl.parse(doc)
    _methods = doc_dsl.methods
    doc_dsl.complie()

    code = doc_dsl.code
    ns = {}
    exec code in ns
    methods = {}

    for name in _methods:
        methods[name] =  ns[name]
    return methods


class DSLWebTestCaseMeta(type):

    def __new__(metacls, cls_name, bases, attrs):
        doc = attrs.get('__doc__')
        if doc:
            test_methods = CommandDslParsertest_methods = gen_test_methods_from_class(doc)
            attrs.update(test_methods)

        cls = type.__new__(metacls, cls_name, bases, attrs)
        return cls


class WebTestCaseMixin(WebTestCase):

    def t(self, doc):
        dsl = CommandDslParser()
        dsl.parse(doc)
        dsl.complie()
        code = dsl.code
        exec(code)


class DSLWebTestCase(with_metaclass(DSLWebTestCaseMeta, (WebTestCaseMixin,))):
    pass

