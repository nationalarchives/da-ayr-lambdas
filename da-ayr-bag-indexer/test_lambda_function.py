import unittest
import os
import lambda_function


class TestLambdaAYRBagIndexer(unittest.TestCase):
    test_event_1 = {
        "s3_bucket": os.getenv('S3_BUCKET'),
        "bag_name": "TDR-2022-D6WD.tar.gz",
        "bag_output_s3_path": "ayr-in/TDR-2022-D6WD.tar.gz",
        "unpacked_files": [
            "ayr-in/TDR-2022-D6WD.tar.gz/TDR-2022-D6WD/bag-info.txt",
            "ayr-in/TDR-2022-D6WD.tar.gz/TDR-2022-D6WD/bagit.txt",
            "ayr-in/TDR-2022-D6WD.tar.gz/TDR-2022-D6WD/data/content/file-c1.txt",
            "ayr-in/TDR-2022-D6WD.tar.gz/TDR-2022-D6WD/data/content/file-c2.txt",
            "ayr-in/TDR-2022-D6WD.tar.gz/TDR-2022-D6WD/data/content/folder-a/file-a1.txt",
            "ayr-in/TDR-2022-D6WD.tar.gz/TDR-2022-D6WD/data/content/folder-a/file-a2.txt",
            "ayr-in/TDR-2022-D6WD.tar.gz/TDR-2022-D6WD/data/content/folder-b/file-b1.txt",
            "ayr-in/TDR-2022-D6WD.tar.gz/TDR-2022-D6WD/data/content/folder-b/file-b2.txt",
            "ayr-in/TDR-2022-D6WD.tar.gz/TDR-2022-D6WD/file-av.csv",
            "ayr-in/TDR-2022-D6WD.tar.gz/TDR-2022-D6WD/file-ffid.csv",
            "ayr-in/TDR-2022-D6WD.tar.gz/TDR-2022-D6WD/file-metadata.csv",
            "ayr-in/TDR-2022-D6WD.tar.gz/TDR-2022-D6WD/manifest-sha256.txt",
            "ayr-in/TDR-2022-D6WD.tar.gz/TDR-2022-D6WD/tagmanifest-sha256.txt"
        ]
    }

    def test_expected_data(self):
        result = lambda_function.lambda_handler(self.test_event_1, None)
        self.assertIn('ayr_role', result)
        self.assertIn('bag_s3_url', result)
        self.assertIn('bag_data', result)
        self.assertIn('bag-info.txt', result['bag_data'])
        self.assertTrue(len(result['bag_data']) == 8)  # 7 root files + 1 bag sub file list
        self.assertTrue(len(result['bag_data']['bag_sub_files']) == 6)
