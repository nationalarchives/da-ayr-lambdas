import os
import boto3


class AYRBagIndexerError(Exception):
    """
    For Lambda errors.
    """


OPENSEARCH_INDEX = os.getenv('AYR_OPENSEARCH_INDEX', default='bag')
KEY_S3_BUCKET = 's3_bucket'
KEY_BAG_NAME = 'bag_name'
KEY_BAG_OUTPUT_S3_PATH = 'bag_output_s3_path'
KEY_UNPACKED_FILES = 'unpacked_files'
BAG_FILE_INFO = 'bag-info'

s3 = boto3.client('s3')


def validate_event(event):
    """
    Raise error if event not valid.

    :param event: AWS Lambda event
    """
    if KEY_S3_BUCKET not in event:
        raise AYRBagIndexerError(f'Key "{KEY_S3_BUCKET} not found"')
    if KEY_BAG_NAME not in event:
        raise AYRBagIndexerError(f'Key "{KEY_BAG_NAME} not found"')
    if KEY_BAG_OUTPUT_S3_PATH not in event:
        raise AYRBagIndexerError(f'Key "{KEY_BAG_OUTPUT_S3_PATH} not found"')
    if KEY_UNPACKED_FILES not in event:
        raise AYRBagIndexerError(f'Key "{KEY_UNPACKED_FILES} not found"')


def s3_object_to_dict(s3_object) -> dict:
    """
    Return S3 object as a dictionary.
    """
    return_dict = {}
    lines = s3_object['Body'].read().decode('utf-8').splitlines()
    for line in lines:
        key, value = line.strip().split(': ', 1)
        return_dict[key] = value
    return return_dict


def process_bag_file(
        s3_bucket: str,
        s3_key: str,
        short_s3_name: str
):
    """
    If given S3 bag file is supported, return its dictionary representation
    and an associated key name (both used to create an associated OpenSearch
    record).

    :param s3_bucket:
    :param s3_key:
    :param short_s3_name:
    :return:
    """
    # Process bag-info.txt
    if short_s3_name == BAG_FILE_INFO + '.txt':
        s3_object = s3.get_object(Bucket=s3_bucket, Key=s3_key)
        bag_info = s3_object_to_dict(s3_object)
        return BAG_FILE_INFO, bag_info

    return None


def lambda_handler(event, context):
    """
    Scan bag files in S3 and return OpenSearch record.

    Expects the following input event format (e.g. from da-ayr-bag-unpacker):

    {
      "s3_bucket": "da-ayr-data",
      "bag_name": "TDR-2022-D6WD.tar.gz",
      "bag_output_s3_path": "ayr-in/TDR-2022-D6WD.tar.gz",
      "unpacked_files": [
        "ayr-in/TDR-2022-D6WD.tar.gz/TDR-2022-D6WD/bag-info.txt",
        "ayr-in/TDR-2022-D6WD.tar.gz/TDR-2022-D6WD/bagit.txt",
        "ayr-in/TDR-2022-D6WD.tar.gz/TDR-2022-D6WD/data/content/file-c1.txt",
        ...
        "ayr-in/TDR-2022-D6WD.tar.gz/TDR-2022-D6WD/file-av.csv",
        "ayr-in/TDR-2022-D6WD.tar.gz/TDR-2022-D6WD/file-ffid.csv",
        "ayr-in/TDR-2022-D6WD.tar.gz/TDR-2022-D6WD/file-metadata.csv",
        "ayr-in/TDR-2022-D6WD.tar.gz/TDR-2022-D6WD/manifest-sha256.txt",
        "ayr-in/TDR-2022-D6WD.tar.gz/TDR-2022-D6WD/tagmanifest-sha256.txt"
      ]
    }

    :param event: AWS Lambda event
    :param context: AWS Lambda context
    :return: AWS Lambda response
    """
    validate_event(event)

    s3_bucket = event[KEY_S3_BUCKET]
    print(f's3_bucket={s3_bucket}')
    bag_name = event[KEY_BAG_NAME]
    print(f'bag_name={bag_name}')
    bag_output_s3_path = event[KEY_BAG_OUTPUT_S3_PATH]
    print(f'bag_output_s3_path={bag_output_s3_path}')
    bag_s3_url = f's3://{s3_bucket}/{bag_output_s3_path}'
    unpacked_files = event[KEY_UNPACKED_FILES]

    opensearch_record = {
        'ayr_role': None,
        'bag_s3_url': bag_s3_url
    }

    for full_s3_name in unpacked_files:
        prefix = bag_output_s3_path + '/' + bag_name.split('.')[0] + '/'
        print(f'remove prefix "{prefix}" from "{full_s3_name}"')
        short_s3_name = full_s3_name.removeprefix(prefix)
        print(f'short_s3_name="{short_s3_name}"')

        opensearch_entry = process_bag_file(
            s3_bucket=s3_bucket,
            s3_key=full_s3_name,
            short_s3_name=short_s3_name
        )

        if opensearch_entry:
            opensearch_record[opensearch_entry[0]] = opensearch_entry[1]

    return opensearch_record
