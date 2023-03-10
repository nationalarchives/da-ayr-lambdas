import unittest
from s3_bag_reader import BagFileMapper
from s3_bag_reader import BagError


class TestBagFileMapper(unittest.TestCase):
    file_list_1 = [
        'foo/bar.tar.gz/bar/bag-info.txt',
        'foo/bar.tar.gz/bar/bagit.txt',
        'foo/bar.tar.gz/bar/data/content/file-c1.txt'
    ]

    def test_expected_data(self):
        BagFileMapper(
            file_list=self.file_list_1,
            path_prefix='foo/bar.tar.gz/bar/'
        )

    def test_expected_error(self):
        try:
            BagFileMapper(
                file_list=[],
                path_prefix='foo/bar.tar.gz/bar/'
            )
        except BagError as e:
            if 'No input file for "bag-info.txt"' not in str(e):
                self.fail('Got error, but not expected message')
