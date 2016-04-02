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


from . import Natume


def get_cmd_options():
    from argparse import ArgumentParser
    parser = ArgumentParser(usage="natume [options]  test_dirs (or files)...")
    parser.add_argument('-u', '--url', help='the url for test', default=None)
    parser.add_argument("-d", "--debug", action='store_true', default=False, help="open debug mode (default %(default)r)")
    parser.add_argument("test_dirs", default=[], nargs='*', help="the test dirs")
    return parser.parse_args()


def console_run():
    options = get_cmd_options()
    paths = options.test_dirs
    url = options.url
    debug = options.debug

    smoke = Natume(url, paths, debug)
    smoke.run()



if __name__ == '__main__':
    console_run()