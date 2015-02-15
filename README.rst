Natume
###########

Natume is a http dsl test tool help you easily build test for mobile application.


How to install
==============

Firstly download or fetch it form github then run the command in shell:

.. code-block:: bash

    cd natume # the path to the project
    python setup.py install


Development
===========

Fork or download it, then run:

.. code-block:: bash 

    cd natume # the path to the project
    python setup.py develop



Compatibility
=============

Built and tested under Python 2.7 


How to write your dsl http test
================================


The dsl rule most like ini file format.


comment
--------------

The line begins with "#" is a comment line





method section
---------------

The line begins with a ``[`` and ends with ``]`` a test method section::


	[add friend]
	# comment
	> POST /request fid=1233 access_token="Blabla"
	code: 200
	content <- OK


intialize your test instance variables
-----------------------------------------

You can intialize or bind the variables use intialize method::

	[intialize]

	@key = "key"
	@page = 2


All key begins with "@" will build to testcase instance attributes, like @key is compiled to  "self.key",
and intialize method  is called in SetUp method.



http send command
--------------------


The line begins with ``>`` is a http request::

	> GET /post key="Blabla"  page=1
	> POST /profile name="Blabla" email="e@e.com"


set request header
---------------------


Sometimes, the request requires to set headers, you can use  "=>"  command to set header ::

	referer => https://www.example.com/
	Referer => https://www.example.com/
	Accept-Encoding => gzip, deflate, sdch
	Accept_encoding => gzip, deflate, sdch


.. Note:: the head key is caseinsentive and key parts can  will auto trasfer to the http real key pattern.

Assert the response
----------------------

Currently, supports content regex match assert, json data assert, and response header assert.
and  supports three assert tokens.

:
^^^^^^^^^^

"":"" assert token, it is compiled to assertEqual method, to check a header or response text, or response json data::


	code: 200
	content_tpye : application/json
	charset: utf-8


<-
^^^^^^^^^^

it is compiled to  assertIn method  in response content test::


	content  <- OK
	json <- ['data']['title'] =  "Blabla"

=~
^^^^^^^^^^


it is compiled to to check a regex text in response content test, the regex value must begins and ends with "/", and can combine with the regex options::

	content  =~ /OK/
	json =~ ['data']['title'] =  /Blabla/i

.. Note:: Currently supports three regex compile options "i"(re.I), "m" (re.M), "s" (re.S).

Test response header info
^^^^^^^^^^^^^^^^^^^^^^^^^^^

When set code command:

	code: 200

it will assert response status code.

When set content_type command:

	content_tpye : application/json

it will assert response content_type.

When set charset command:

	charset:  utf-8

it will assert response charset.


.. Note:: When uses ":" to test response info, if the assert key not in (content, json, code, content_type, charset)， it will test the response head info.



content
^^^^^^^^^^^

when we test the response text, supports the  commands as below::

	content: OK
	content <- OK
	content =~ /Ok/i


json
~~~~~~~~~


When we  test the response is json data, we can use json key to assert::



	json <- ['data']['title'] =  'title'
	json: ['data']['trackList'][0]['song_id'] =  '1772167572'
	json: ['data']['type_id'] = 1



DSLWebTestCase
=================


When you wanna write the dsl test in unittest testcase, please write test method in testcase class doc:



.. code-block:: python


	from natume import DSLWebTestCase, WebClient
	import unittest

	class DSLWebTestCaseTest(DSLWebTestCase):
	    u"""
	    [index]
	    > GET /

	    content <- 虾米音乐网(xiami.com)


	    [song api]
	    > GET /song/playlist/id/1772167572/type/0/cat/json

	    content_type: application/json
	    charset: utf-8

	    json: ['data']['trackList'][0]['title'] = u'再遇见'
	    json: ['data']['trackList'][0]['song_id'] =  '1772167572'
	    json: ['data']['type_id'] = 1

	    [search]
	    > GET /search/collect key='苏打绿'

	    code: 200
	    content <- 苏打绿歌曲: 最好听的苏打绿音乐试听
	    content =~ /Xiami.com/i


	    [search page 2]
	    > GET /search/collect/page/2 key=@key order='weight'

	    code: 200
	    content <- 苏打绿歌曲: 最好听的苏打绿音乐试听
	    content =~ /XiaMi.com/i
	    """
	    @classmethod
	    def setUpClass(self):
	        self.client =  WebClient('http://www.xiami.com')
	        self.key = '苏打绿'

	    def test_t(self):
	        self.t(u"""
	            > GET /search/collect/page/2 key=@key order='weight'

	            code: 200
	            content <- 苏打绿歌曲: 最好听的苏打绿音乐试听
	            """)


You can also use ``t`` method to  build request section test.


.. Note:: The WebClient will keep and fresh the cookies and etag  when you use a same  webclient to test your application.



Run test in  terminal
==========================


Like unittest, natume can run in  terminal also, can test directories and files.

.. code-block bash

	python -m natume -h
	usage: natume [options]  test_dirs (or files)...

	positional arguments:
	  test_dirs          the test dirs

	optional arguments:
	  -h, --help         show this help message and exit
	  -u URL, --url URL  the url for test
	  -d, --debug        open debug mode (default False)


Here are the demos, the test file in project examples directory:

.. code-block:: bash

	$ python -m natume -u http://www.xiami.com examples/xiami.smoke  -d
	test_index (__builtin__.XiamiTest) ... ok
	test_search (__builtin__.XiamiTest) ... ok
	test_search_page_2 (__builtin__.XiamiTest) ... ok
	test_song_api (__builtin__.XiamiTest) ... ok

	----------------------------------------------------------------------
	Ran 4 tests in 0.674s

	OK


.. code-block:: bash

	$ python -m natume -u http://www.xiami.com  examples -d
	test_index (__builtin__.XiamiTest) ... ok
	test_search (__builtin__.XiamiTest) ... ok
	test_search_page_2 (__builtin__.XiamiTest) ... ok
	test_song_api (__builtin__.XiamiTest) ... ok

	----------------------------------------------------------------------
	Ran 8 tests in 2.893s

	OK


LICENSE
=======

    Copyright (C) 2015 Thomas Huang

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, version 2 of the License.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.

