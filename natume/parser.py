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


""" The `natume.paser` provider the dsl test file paser, it parses and builds the dsl to Test Case Class

the line rules::

    test case class name::

        firstly it builds a test case class name based the file prefix name like 'test.smoke' , it named TestTest

    the method section::

        the section like '[index]' is a test method section , builds to def test_index(self):

    the send command::

        all the line start with a '>' is send request command.

        rule::

            > $METHOD $PATH  $PAYLOAD

        Example::

            > POST /login user='test_user' pass=@pass
            > GET /index

    the assert line:
        the line inclue (':' , '<-', '=~')

the variable rule::

    the variable:

        the key start with '@' is the test case instance attribute

    the set header:

        the line include '=>' will build in headers dict

    the regex assert s:
        when the value start and  end with '/' will build to a regex check assert
"""

import re
import codecs
import os.path


class BaseParser(object):

    COMMAND_TOKEN = '>'
    SET_HEADER_TOKEN = '=>'
    ASSERT_TOKENS = (':', '<-', '=~', '~~')
    SET_VAR_TOKEN = '='
    VAR_TOKEN = '@'

    VAR_REGEX = re.compile(r'%s[a-zA-Z_][a-zA-Z0-9_]+' % (VAR_TOKEN))
    SETCTION_REGEX = re.compile(r'\[\s*?(.+)\s*?\]')
    SET_HEADER_REGEX = re.compile(r'([a-zA-Z0-9_]+)\s*%s\s*(.*)' % (SET_HEADER_TOKEN))
    ASSERT_REGEX = re.compile(r'([a-zA-Z0-9_]+)\s*(%s)\s*(.*)' % ('|'.join(ASSERT_TOKENS)))
    ASSIGN_REGEX = re.compile(r'%s([a-zA-Z_][a-zA-Z0-9_]+)\s*%s\s*(.*)' % (VAR_TOKEN, SET_VAR_TOKEN))

    def complie(self):
        self.scope.write(self.writer)

    @property
    def code(self):
        return self.writer.code

    def parse(self, *args, **kw):
        raise NotImplementedError('Must implement in subclass')

    def parse_line(self, line, lineno):
        line = line.strip()
        if not line or line.startswith('#'):
            return

        # smoke section handle
        m = self.SETCTION_REGEX.match(line)
        if m:
            if self.current_section:
                self.scope.add_node(self.current_section)

            name = '_'.join([i for i in m.group(1).split(' ') if i.strip()])

            self.current_section = MethodScope(name)
            return

        if line.startswith(self.COMMAND_TOKEN):
            chunk = re.split(' +', line, 3)
            method, path = chunk[1], chunk[2]
            payload = {}
            if len(chunk) == 4:
                data = chunk[3]
                data = re.sub(r'=\s*%s([a-zA-Z_][a-zA-Z0-9_]+)' % (self.VAR_TOKEN), r'=self.\1', data)
                data = data.split()
                for i in data:
                    k, v = i.split('=')
                    payload[k] = v
            self.current_section.add_node(CommandScope(method, path, payload))
            return

        m = self.SET_HEADER_REGEX.match(line)
        if m:
            head, value = m.group(1), m.group(2)
            self.current_section.nodes[-1].headers.append((head, value))
            return

        m = self.ASSERT_REGEX.match(line)
        if m:
            key, op, value = m.group(1), m.group(2), m.group(3)
            assert_command = AssertCommand(key, op, value, line, lineno)
            self.current_section.nodes[-1].asserts.append(assert_command)
            return

        m = self.ASSIGN_REGEX.match(line)
        if m:
            key, value = m.group(1), m.group(2)
            key = 'self.' + key
            self.current_section.var_nodes.append((key, value))


class DSLParser(BaseParser):

    def __init__(self):
        self.current_section = None
        self.current_command = None
        self.writer = Writer()
        self.class_name = None
        self.scope = None

    def parse(self, path, filename):
        filepath = os.path.join(path, filename)
        fp = codecs.open(filepath, "r", "utf-8")
        lineno = 0
        class_name = filename.split('.', 1)[0]
        self.class_name = self._class_name(class_name)
        self.scope = ClassScope(self.class_name)

        while True:
            line = fp.readline()
            if not line:
                break
            lineno += 1
            self.parse_line(line, lineno)

        if self.current_section:
            self.scope.add_node(self.current_section)

        fp.close()

    def _class_name(self, name):
        parts = re.split(r'[_-]', name.lower())
        parts = [_.capitalize() for _ in parts]
        return ''.join(parts) + 'Test'


class DocDSLParser(BaseParser):

    def __init__(self):
        self.current_section = None
        self.current_command = None
        self.methods = []
        self.writer = Writer()
        self.scope = DocMethodsScpoe()

    def parse(self, string, lineno=0):

        lines = string.split('\n')
        for line in lines:
            self.parse_line(line, lineno)
            lineno += 1
        if self.current_section:
            self.scope.add_node(self.current_section)

        for method_scope in self.scope.nodes:
            self.methods.append('test_' + method_scope.name)


class CommandDslParser(BaseParser):

    def __init__(self):
        self.current_command = None
        self.writer = Writer()
        self.current_section = CommandsScope()

    def parse(self, string, lineno=0):

        lines = string.split('\n')
        for line in lines:
            self.parse_line(line, lineno)
            lineno += 1

    def parse_line(self, line, lineno):
        line = line.strip()
        if not line or line.startswith('#'):
            return

        if line.startswith(self.COMMAND_TOKEN):
            chunk = re.split(' +', line, 3)
            method, path = chunk[1], chunk[2]
            payload = {}
            if len(chunk) == 4:
                data = chunk[3]
                data = re.sub(r'=\s*%s([a-zA-Z_][a-zA-Z0-9_]+)' % (self.VAR_TOKEN), r'=self.\1', data)
                data = data.split()
                for i in data:
                    k, v = i.split('=')
                    payload[k] = v
            self.current_section.add_node(CommandScope(method, path, payload))
            return

        m = self.SET_HEADER_REGEX.match(line)
        if m:
            head, value = m.group(1), m.group(2)
            self.current_section.nodes[-1].headers.append((head, value))
            return

        m = self.ASSERT_REGEX.match(line)
        if m:
            key, op, value = m.group(1), m.group(2), m.group(3)
            assert_command = AssertCommand(key, op, value, line, lineno)
            self.current_section.nodes[-1].asserts.append(assert_command)
            return

        m = self.ASSIGN_REGEX.match(line)
        if m:
            key, value = m.group(1), m.group(2)
            key = 'self.' + key
            self.current_section.var_nodes.append((key, value))

    def complie(self):
        self.current_section.write(self.writer)

    @property
    def code(self):
        return self.writer.code


class BaseScope(object):

    def __init__(self, indent=0, node=None):
        self.indent = indent
        self.nodes = [node] if node else []

    def add_node(self, node):
        self.nodes.append(node)


class ClassScope(BaseScope):

    def __init__(self, name, base_class='WebTestCase', indent=0, node=None):
        BaseScope.__init__(self, indent, node)
        self.name = name
        self.base_class = base_class

    def write(self, writer):
        writer.puts('class %s(%s):\n' % (self.name, self.base_class))
        indent = self.indent + 1
        self.write_setup_method(writer, indent)
        for node in self.nodes:
            node.write(writer, indent)

    def write_setup_method(self, writer, indent):
        writer.puts('def setUp(self):', indent)
        writer.puts('self.client = client', indent + 1)
        writer.puts('self.initialize()', indent + 1)


class DocMethodsScpoe(BaseScope):

    def write(self, writer, indent=0):
        indent = indent or self.indent
        for node in self.nodes:
            node.write(writer, indent)


class CommandsScope(BaseScope):

    def __init__(self, indent=0, node=None):
        BaseScope.__init__(self, indent, node)
        self.var_nodes = []

    def write(self, writer, indent=None):
        indent = indent or self.indent
        writer.puts('')
        for node in self.nodes:
            node.write(writer, indent)
        if not self.nodes:
            writer.puts('pass', indent)


class MethodScope(BaseScope):

    def __init__(self, name, indent=0, node=None):
        BaseScope.__init__(self, indent, node)
        self.name = name
        self.var_nodes = []

    def write(self, writer, indent=None):
        indent = indent or self.indent
        writer.puts('')
        if self.name == 'initialize':
            writer.puts('def initialize(self):', indent)
            indent += 1
            for key, value in self.var_nodes:
                writer.puts('%s=%s' % (key, value), indent)
            return

        writer.puts('def test_%s(self):' % (self.name), indent)
        indent += 1

        for node in self.nodes:
            node.write(writer, indent)

        if not self.nodes:
            writer.puts('pass', indent)


class CommandScope(BaseScope):

    def __init__(self, method, path, data=None, indent=None, node=None):
        BaseScope.__init__(self, indent, node)
        self.asserts = []
        self.headers = []
        self.sets = []
        self.path = path
        self.data = data or {}
        self.method = method

    def write(self, writer, indent):
        writer.puts('headers = {}', indent)
        for k, v in self.headers:
            k = self.format_header_key(k)
            writer.puts('headers[%r] = %r' % (k, v), indent)

        writer.puts('data = {}', indent)
        for k, v in self.data.items():
            writer.puts('data[%r] = %s' % (k, v), indent)
        writer.puts('self.client.do_request(%r, %r, data, headers)\n' % (self.method, self.path), indent)

        for assert_command in self.asserts:
            assert_command.write(writer, indent)

    def format_header_key(self, key):
        parts = re.split(r'[_-]', key.lower())
        parts = [_.capitalize() for _ in parts]
        return '-'.join(parts)

    def __str__(self):
        return '<CommandScope method : %s, nodes:%d>' % (self.method, len(self.nodes))


class BaseCommand(object):

    def __init__(self, indent=0):
        self.indent = indent

    def write(self, writer, indent):
        pass


class AssertCommand(BaseCommand):

    def __init__(self, key, op, value, line, lineno, indent=0):
        BaseCommand.__init__(self, indent)
        self.key = key
        self.op = op
        self.value = value
        self.line = line
        self.lineno = lineno

    def write(self, writer, indent=None):
        indent = indent if indent is not None else self.indent
        assert_key = self._key(self.key)

        if assert_key in ('Status', 'Code', 'ContentType', 'Charset'):
            self._line(writer, 'self.assert%s(%r)' % (assert_key, self.value), indent)

        elif assert_key == 'Json':
            key, value = self.value.split("=")

            key = key.strip()
            value = value.strip()
            writer.puts("json = self.client.json", indent)
            if key:
                writer.puts("json = json%s" % (key), indent)
            self._line(writer, 'self.assertJson(json, %r, %s)' % (self.op, value), indent)

        elif assert_key == 'Content':
            self._line(writer, 'self.assertContent(%r, %r)' % (self.op, self.value), indent)

        elif self.op == ':':
            if assert_key not in ('Content', 'Json'):
                key = self._key(self.key)
                self._line(writer, 'self.assertHeader(%r, %r)' % (key, self.value), indent)
        else:
            key = self._key(self.key)
            self._line(writer, 'self.assertHeader(%r, %r, %r)' % (key, self.op, self.value), indent)

    def _line(self, writer, line, indent):
        writer.puts(line + " # lineno " + str(self.lineno) + ": " + self.line, indent)

    def _key(self, k):
        parts = re.split(r'[_-]', k.lower())
        parts = [_.capitalize() for _ in parts]
        return ''.join(parts)


class Writer(object):

    def __init__(self):
        self.code = ''
        self.indent = 0

    def puts(self, line, indent=None):
        indent = indent or self.indent
        self.write('\t' * indent + line + '\n')

    def write(self, text):
        self.code += text
