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


import sys


PY_MAJOR = sys.version_info[0]
PY_MINOR = sys.version_info[1]
PY2 = PY_MAJOR == 2

if PY2:  # pragma: nocover

    from cStringIO import StringIO as BytesIO
    from Cookie import SimpleCookie  # noqa
else:  # pragma: nocover
    from io import BytesIO
    from http.cookies import SimpleCookie


GzipFile = __import__('gzip', None, None, ['GzipFile']).GzipFile

if PY2 and PY_MINOR < 7:  # pragma: nocover
    __saved_GzipFile__ = GzipFile

    def GzipFile(filename=None, mode=None, compresslevel=9,
                 fileobj=None, mtime=None):
        return __saved_GzipFile__(filename, mode, compresslevel,
                                  fileobj)