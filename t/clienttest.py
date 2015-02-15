import unittest
from natume.client import WebClient


class WebClientTest(unittest.TestCase):

    def setUp(self):
        self.client = WebClient('https://www.bing.com')

    def test_get(self):
        self.client.get('/')
        self.assertEqual(self.client.charset, 'utf-8')
        self.assertEqual(self.client.content_type, 'text/html')

if __name__ == "__main__":
    unittest.main()
