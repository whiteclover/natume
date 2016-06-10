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
#!/usr/bin/env python


"""The module provides the HTTP/HTTPS Client class,
it can handle the http(s) request and return the response and other response property access unities
"""

import urllib2
import base64
from natume.connection import HTTPConnection, HTTPSConnection, urlsplit, urljoin, urlencode
from natume.util import decompress
from natume.compat import SimpleCookie
from json import loads


class WebClient(object):

    DEFAULT_HEADERS = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.114 Safari/537.36',
        'Accept-Encoding': 'gzip',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
    }

    def __init__(self, url, headers=None, auth=None, ca=None):
        scheme, uri, path, query, fragment = urlsplit(url)
        http_class = scheme == 'http' and HTTPConnection or HTTPSConnection
        self.connection = http_class(uri)
        self.default_headers = self.DEFAULT_HEADERS.copy()

        if headers:
            self.default_headers.update(headers)
        self.path = path
        self.headers = {}
        self.cookies = {}
        self.etags = {}
        self.status_code = 0
        self.body = None
        self.__content = None
        self.__json = None

        self.auth = auth

    def ajax(self, method, path, headers=None, **kwargs):
        """ GET HTTP AJAX request."""
        headers = headers or {}
        headers['X-Requested-With'] = 'XMLHttpRequest'
        return self.do_request(method, path, headers=headers, **kwargs)

    def get(self, path, **kwargs):
        """ GET HTTP request."""
        return self.do_request('GET', path, **kwargs)

    def head(self, path, **kwargs):
        """ HEAD HTTP request."""
        return self.do_request('HEAD', path, **kwargs)

    def post(self, path, **kwargs):
        """ POST HTTP request."""
        return self.do_request('POST', path, **kwargs)

    def follow(self):
        sc = self.status_code
        assert sc in [207, 301, 302, 303, 307]
        location = self.headers['location'][0]
        scheme, netloc, path, query, fragment = urlsplit(location)
        method = sc == 307 and self.method or 'GET'
        return self.do_request(method, path)

    def do_request(self, method, path, payload=None, headers=None, auth=None):

        request_header = self.default_headers.copy()
        if headers:
            request_header.update(headers)

        auth = auth or self.auth
        if auth:
            self.handle_auth_header(auth[0], auth[1])

        if self.cookies:
            request_header['Cookie'] = '; '.join(
                '%s=%s' % cookie for cookie in self.cookies.items())
        path = urljoin(self.path, path)

        if path in self.etags:
            request_header['If-None-Match'] = self.etags[path]

        body = ''
        if payload:
            if method == 'GET':
                path += '?' + urlencode(payload, doseq=True)
            else:
                body = urlencode(payload, doseq=True)
                request_header['Content-Type'] = 'application/x-www-form-urlencoded'

        self.status_code = 0
        self.body = None

        self.__content = None
        self.__json = None

        self.connection.connect()
        self.connection.request(method, path, body, request_header)
        r = self.connection.getresponse()
        self.body = r.read()
        self.connection.close()

        self.status_code = r.status
        self.headers = {}
        for name, value in r.getheaders():
            self.headers[name] = value

        self.handle_content_encoding()
        self.handle_etag(path)
        self.handle_cookies()
        return self.status_code

    def handle_auth_header(self, username, password):
        auth_base64 = base64.encodestring('%s:%s' % (username, password)).replace('\n', '')
        self.headers["Authorization"] = "Basic %s" % (auth_base64)

    def handle_content_encoding(self):
        if 'content-encoding' in self.headers \
                and 'gzip' in self.headers['content-encoding']:
            self.body = decompress(self.body)

    def handle_etag(self, path):
        """Etags process"""
        if 'etag' in self.headers:
            self.etags[path] = self.headers['etag'][-1]

    def handle_cookies(self):
        if 'set-cookie' in self.headers:
            cookie_string = self.headers['set-cookie']
            cookies = SimpleCookie(cookie_string)
            for name in cookies:
                value = cookies[name].value
                if value:
                    self.cookies[name] = value
                elif name in self.cookies:
                    del self.cookies[name]

    def clear_cookies(self):
        """Clear cookies"""
        self.cookies = {}

    @property
    def content(self):
        """ Returns a content of the response.
        """
        if self.__content is None:
            self.__content = self.body.decode('utf-8')
        return self.__content

    @property
    def json(self):
        """ Returns a json response."""
        assert 'application/json' in self.headers['content-type']
        if self.__json is None:
            self.__json = loads(self.body)
        return self.__json

    def show(self):
        """Opens the current page in real web browser."""
        with open('page.html', 'w') as fp:
            fp.write(self.body)
        import webbrowser
        import os
        url = 'file://' + os.path.abspath('page.html')
        webbrowser.open(url)

    def get_header(self, key):
        """Get header value"""
        key = key.replace('_', '-')
        if key in self.headers:
            return self.headers[key]

    @property
    def content_type(self):
        """Get Content type"""
        value = self.get_header('content-type')
        c = value.split(';')
        return c[0]

    @property
    def charset(self):
        """Get http chaset encoding"""
        value = self.get_header('content-type')
        c = value.split(';')
        if len(c) == 2:
            return c[1].split('=')[1]
