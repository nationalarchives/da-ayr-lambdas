import os
import tar_lib


class AYRBagUnpackerError(Exception):
    """
    For Lambda errors.
    """


S3_OUTPUT_PREFIX = os.getenv('AYR_S3_OUTPUT_PREFIX', default='ayr-in/')
PATH_JOIN = '/'
KEY_S3_BUCKET = 's3_bucket'
KEY_BAG_NAME = 'bag_name'
KEY_BAG_OUTPUT_S3_PATH = 'bag_output_s3_path'


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
    print(f'event:\n{event}')
    print(f'context:\n{context}')

    if KEY_S3_BUCKET not in event:
        raise AYRBagUnpackerError(f'Key "{KEY_S3_BUCKET} not found"')
    if KEY_BAG_NAME not in event:
        raise AYRBagUnpackerError(f'Key "{KEY_BAG_NAME} not found"')
    if KEY_BAG_OUTPUT_S3_PATH not in event:
        raise AYRBagUnpackerError(f'Key "{KEY_BAG_OUTPUT_S3_PATH} not found"')

    s3_bucket = event[KEY_S3_BUCKET]
    bag_name = event[KEY_BAG_NAME]
    bag_output_s3_path = event[KEY_BAG_OUTPUT_S3_PATH]

    extracted_object_names = tar_lib.untar_s3_object(
        input_bucket_name=s3_bucket,
        output_bucket_name=s3_bucket,
        object_name=bag_output_s3_path,
        output_prefix=S3_OUTPUT_PREFIX + bag_name + PATH_JOIN
    )

    response = {
        's3_bucket': s3_bucket,
        'bag_name': bag_name,
        'bag_output_s3_path': bag_output_s3_path,
        'unpacked_files': extracted_object_names
    }

    return response
