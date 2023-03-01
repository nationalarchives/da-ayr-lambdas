import unittest
import lambda_function


class TestLambdaAYRBagRoleAssigner(unittest.TestCase):
    test_event_1 = {
        "ayr_role": None,
        "bag_s3_url": "s3://...redacted.../ayr-in/TDR-2022-D6WD.tar.gz",
        "bag_data": {
            "bag-info.txt": {
                "Consignment-Type": "standard",
                "Bag-Creator": "TDRExportv0.0.166",
                "Consignment-Start-Datetime": "2022-11-11T10:18:41Z",
                "Consignment-Series": "TSTA 1",
                "Source-Organization": "Testing A",
                "Contact-Name": "Paul Young",
                "Internal-Sender-Identifier": "TDR-2022-D6WD",
                "Consignment-Completed-Datetime": "2022-11-11T10:28:49Z",
                "Consignment-Export-Datetime": "2022-11-11T10:29:39Z",
                "Contact-Email": "paul.young@something2.com",
                "Payload-Oxum": "252.6",
                "Bagging-Date": "2022-11-11"
            },
            "bagit.txt": {}
        }
    }

    def test_expected_data(self):
        result = lambda_function.lambda_handler(self.test_event_1, None)
        self.assertIn('ayr_role', result)
        self.assertIn('bag_s3_url', result)
        self.assertIn('bag_data', result)
        self.assertTrue(len(result) == 3)
        self.assertEqual(result['ayr_role'], 'department_a_role')
