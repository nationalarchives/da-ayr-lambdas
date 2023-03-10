import os
import object_lib
from urllib.parse import urlparse


class AYRBagReceiverError(Exception):
    """
    Used to indicate an AYR bag receiver specific error condition.
    """


S3_OUTPUT_BUCKET = os.getenv('AYR_TARGET_S3_BUCKET')
if not S3_OUTPUT_BUCKET:
    raise AYRBagReceiverError('AYR_TARGET_S3_BUCKET not set')
S3_OUTPUT_PREFIX = os.getenv('AYR_TARGET_S3_OUTPUT_PREFIX', default='ayr-in/')

print(f'S3_OUTPUT_BUCKET={S3_OUTPUT_BUCKET}')
print(f'S3_OUTPUT_PREFIX={S3_OUTPUT_PREFIX}')

KEY_TRE_EVENT = 'dri-preingest-sip-available'
KEY_BAG_URL = 'bag-url'


def lambda_handler(event, context):
    """
    Save bag from incoming event's pre-signed URL field to S3.

    This method expects the following input event format (a simplified version
    of a TRE event for alpha demonstration purposes):

    {
        "dri-preingest-sip-available":
            "bag-url": ""
        }
    }

    :param event: AWS Lambda event
    :param context: AWS Lambda context
    :return: AWS Lambda response
    """
    print(f'event:\n{event}')
    print(f'context:\n{context}')

    if KEY_TRE_EVENT not in event:
        raise AYRBagReceiverError(f'Key "{KEY_TRE_EVENT} not found"')

    tre_event = event[KEY_TRE_EVENT]

    if KEY_BAG_URL not in tre_event:
        raise AYRBagReceiverError(f'Key "{KEY_BAG_URL} not found"')

    bag_url = tre_event[KEY_BAG_URL]
    print(f'bag_url={bag_url}')

    bag_name = os.path.basename(urlparse(bag_url).path)
    print(f'bag_name={bag_name}')

    bag_output_s3_path = S3_OUTPUT_PREFIX + bag_name
    print(f'bag_output_s3_path={bag_output_s3_path}')

    object_lib.url_to_s3_object(
        source_url=bag_url,
        target_bucket_name=S3_OUTPUT_BUCKET,
        target_object_name=bag_output_s3_path,
        allow_overwrite=False
    )

    response = {
        's3_bucket': S3_OUTPUT_BUCKET,
        'bag_name': bag_name,
        'bag_output_s3_path': bag_output_s3_path
    }

    print(f'response:\n{response}')
    return response
