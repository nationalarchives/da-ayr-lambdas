class AYRBagUnpackerError(Exception):
    """
    For Lambda errors.
    """


def lambda_handler(event, context):
    """
    Unpack specified bag in S3 into a S3 sub-path.

    Expects the following input event format (e.g. from da-ayr-bag-receiver):

    {
        "s3_bucket": "",
        "bag_name": "",
        "bag_output_s3_path": ""
    }

    :param event: AWS Lambda event
    :param context: AWS Lambda context
    :return: AWS Lambda response
    """
    response = {
        'statusCode': 200,
        'body': {}
    }

    return response
