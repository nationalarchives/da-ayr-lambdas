import unittest
import json
import lambda_function


class TestLambdaAYRBagToOpenSearch(unittest.TestCase):
    def test_expected_data(self):
        with open('test_input_event.json') as json_file:
            event = json.load(json_file)
            result = lambda_function.lambda_handler(event, None)
            self.assertIn('statusCode', result)
            self.assertIn('body', result)
