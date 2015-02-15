import unittest

class TestLazyAttr(unittest.TestCase):
    def _makeOne(self, wrapped):
        from natume.util import lazy_attr
        return lazy_attr(wrapped)

    def test___get__withinst(self):
        def wrapped(inst):
            return 'a'
        decorator = self._makeOne(wrapped)
        inst = Dummy()
        result = decorator.__get__(inst)
        self.assertEqual(result, 'a')
        self.assertEqual(inst.__dict__['wrapped'], 'a')

    def test___get__noinst(self):
        decorator = self._makeOne(None)
        result = decorator.__get__(None)
        self.assertEqual(result, decorator)

    def test___doc__copied(self):
        def wrapped(inst):
            """My doc"""
        decorator = self._makeOne(wrapped)
        self.assertEqual(decorator.__doc__, "My doc")

class Dummy(object):
    pass


if __name__ == '__main__':
    unittest.main()