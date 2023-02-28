import os
import unittest
import boto3
import lambda_function

s3 = boto3.client('s3')


class TestLambdaAYRBagReceiver(unittest.TestCase):
    def setUp(self):
        presigned_url = s3.generate_presigned_url(
            ClientMethod='get_object',
            Params={
                'Bucket': os.getenv('AYR_TARGET_S3_BUCKET'),
                'Key': os.getenv('S3_KEY')
            },
            ExpiresIn=60
        )

        self.test_event_1 = {
            "dri-preingest-sip-available": {
                "bag-url": presigned_url
            }
        }

    def test_expected_data(self):
        result = lambda_function.lambda_handler(self.test_event_1, None)
        print(result)
        self.assertIn('s3_bucket', result)
        self.assertIn('bag_name', result)
        self.assertIn('bag_output_s3_path', result)
        self.assertTrue(len(result) == 3)
