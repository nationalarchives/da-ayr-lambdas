import boto3
import s3_bag_reader


class AYRBagIndexerError(Exception):
    """
    For Lambda errors.
    """


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


def lambda_handler(event, context):
    """
    Scan bag files in S3 and return OpenSearch record in the following format:

    {
        'ayr_role': None,
        'bag_s3_url': 'ayr-in/TDR-2022-D6WD.tar.gz',
        'bag_data': {
            'bag-info.txt': { ... },
            ...
            'bag_sub_files' [
                {
                    'object': 'ayr-in/TDR-2022-D6WD.tar.gz/TDR-2022-D6WD/data/content/file-c1.txt',
                    'data': 'dummy data in sample for file-c1.txt'
                },
                ...
            ]
        }
    }

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
    print(f'event={event}')
    print(f'context={context}')
    validate_event(event)
    print('event validated')
    s3_bucket = event[KEY_S3_BUCKET]
    print(f's3_bucket={s3_bucket}')
    bag_name = event[KEY_BAG_NAME]
    print(f'bag_name={bag_name}')
    bag_output_s3_path = event[KEY_BAG_OUTPUT_S3_PATH]
    print(f'bag_output_s3_path={bag_output_s3_path}')
    unpacked_file_list = event[KEY_UNPACKED_FILES]
    bag_s3_url = f's3://{s3_bucket}/{bag_output_s3_path}'
    print(f'bag_s3_url={bag_s3_url}')
    bag_unpack_folder = bag_name.removesuffix('.tar.gz')
    path_prefix = bag_output_s3_path + '/' + bag_unpack_folder + '/'

    bag = s3_bag_reader.S3BagReader(
        s3_bucket=s3_bucket,
        file_list=unpacked_file_list,
        path_prefix=path_prefix
    )

    bag_data = {}
    bag_data.update(bag.get_bag_info_txt_as_dict())
    bag_data.update(bag.get_bagit_txt_as_dict())
    bag_data.update(bag.get_file_av_csv_as_dict())
    bag_data.update(bag.get_file_ffid_csv_as_dict())
    bag_data.update(bag.get_file_metadata_csv_as_dict())
    bag_data.update(bag.get_manifest_sha256_as_dict())
    bag_data.update(bag.get_tagmanifest_sha256_as_dict())
    bag_data.update(bag.get_sub_files_dict())

    opensearch_record = {
        'ayr_role': None,
        'bag_s3_url': bag_s3_url,
        'bag_data': bag_data
    }

    return opensearch_record
