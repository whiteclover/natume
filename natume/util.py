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


from .compat import GzipFile, BytesIO, import_module_from_file


def compress(data, compresslevel=9):
    """ Compress data in one shot.
    """
    s = BytesIO()
    f = GzipFile(fileobj=s, mode='wb', mtime=0)
    f.write(data)
    f.close()
    return s.getvalue()


def decompress(data):
    """ Decompress data in one shot.
    """
    return GzipFile(fileobj=BytesIO(data), mode='rb').read()


class lazy_attr(object):

    def __init__(self, wrapped):
        self.wrapped = wrapped
        try:
            self.__doc__ = wrapped.__doc__
        except:  # pragma: no cover
            pass

    def __get__(self, inst, objtype=None):
        if inst is None:
            return self
        val = self.wrapped(inst)
        setattr(inst, self.wrapped.__name__, val)
        return val
