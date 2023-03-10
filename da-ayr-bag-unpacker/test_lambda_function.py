import os
import unittest
import boto3
import lambda_function

s3 = boto3.client('s3')


class TestLambdaAYRBagUnpacker(unittest.TestCase):
    test_event_1 = {
        "s3_bucket": os.getenv('S3_BUCKET'),
        "bag_name": "TDR-2022-D6WD.tar.gz",
        "bag_output_s3_path": "ayr-in/TDR-2022-D6WD.tar.gz"
    }

    def test_expected_data(self):
        result = lambda_function.lambda_handler(self.test_event_1, None)
        print(result)
        self.assertIn('s3_bucket', result)
        self.assertIn('bag_name', result)
        self.assertIn('bag_output_s3_path', result)
        self.assertIn('unpacked_files', result)
        self.assertTrue(len(result['unpacked_files']) == 13)  # 7 root files + 6 bag sub file list
