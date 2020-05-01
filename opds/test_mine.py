from filesystem import LocalMetadataFileSystem
import unittest

__author__ = 'lei'

fs = LocalMetadataFileSystem()


class MineTest(unittest.TestCase):

    def test_exists(self):
        self.assertTrue(fs.exists(u'\u79d1\u6280'))


if __name__ == "__main__":
    unittest.main()
