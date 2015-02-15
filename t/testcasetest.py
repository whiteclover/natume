# -*- coding: utf-8 -*-


from natume.client import WebClient
from natume import WebTestCase, DSLWebTestCase, WebClient
import unittest


class WebTestCaseTest(WebTestCase):

    def setUp(self):
        self.client = WebClient('http://www.xiami.com')
        self.initialize()

    def initialize(self):
        self.key="苏打绿"

    def test_index(self):
        headers = {}
        data = {}
        self.client.do_request(u'GET', u'/', data, headers)

        self.assertContent(u'<-', u'虾米音乐网(xiami.com)') # lineno 8: content <- 虾米音乐网(xiami.com)

    def test_song_api(self):
        headers = {}
        data = {}
        self.client.do_request(u'GET', u'/song/playlist/id/1772167572/type/0/cat/json', data, headers)

        self.assertContentType(u'application/json') # lineno 14: content_type: application/json
        self.assertCharset(u'utf-8') # lineno 15: charset: utf-8
        json = self.client.json
        json = json['data']['trackList'][0]['title']
        self.assertJson(json, u':', u'再遇见') # lineno 17: json: ['data']['trackList'][0]['title'] = u'再遇见'
        json = self.client.json
        json = json['data']['trackList'][0]['song_id']
        self.assertJson(json, u':', '1772167572') # lineno 18: json: ['data']['trackList'][0]['song_id'] =  '1772167572'
        json = self.client.json
        json = json['data']['type_id']
        self.assertJson(json, u':', 1) # lineno 19: json: ['data']['type_id'] = 1

    def test_search(self):
        headers = {}
        data = {}
        data[u'key'] = '苏打绿'
        self.client.do_request(u'GET', u'/search/collect', data, headers)

        self.assertCode(u'200') # lineno 24: code: 200
        self.assertContent(u'<-', u'苏打绿歌曲: 最好听的苏打绿音乐试听') # lineno 25: content <- 苏打绿歌曲: 最好听的苏打绿音乐试听
        self.assertContent(u'=~', u'/Xiami.com/i') # lineno 26: content =~ /Xiami.com/i

    def test_search_page_2(self):
        headers = {}
        data = {}
        data[u'order'] = 'weight'
        data[u'key'] = self.key
        self.client.do_request(u'GET', u'/search/collect/page/2', data, headers)

        self.assertCode(u'200') # lineno 32: code: 200
        self.assertContent(u'<-', u'苏打绿歌曲: 最好听的苏打绿音乐试听') # lineno 33: content <- 苏打绿歌曲: 最好听的苏打绿音乐试听
        self.assertContent(u'=~', u'/XiaMi.com/i') # lineno 34: content =~ /XiaMi.com/i

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

if __name__ == '__main__':
    unittest.main()