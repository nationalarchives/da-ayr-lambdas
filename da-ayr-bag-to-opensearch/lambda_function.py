import os
import boto3
import requests
import json


class AYRBagToOpenSearchError(Exception):
    """
    For Lambda errors.
    """


ENV_DO_NOT_VERIFY_SSL = 'DO_NOT_VERIFY_SSL'  # e.g. set to TRUE for local testing via ssh tunnel
ENV_OPENSEARCH_HOST_URL = 'OPENSEARCH_HOST_URL'
ENV_OPENSEARCH_INDEX = 'OPENSEARCH_INDEX'
ENV_OPENSEARCH_USER = 'OPENSEARCH_USER'
ENV_OPENSEARCH_USER_PASSWORD = 'OPENSEARCH_USER_PASSWORD'  # local testing only
ENV_OPENSEARCH_USER_PASSWORD_PARAM_STORE_KEY = 'OPENSEARCH_USER_PASSWORD_PARAM_STORE_KEY'
ENV_OPENSEARCH_DEFAULT_INDEX = 'OPENSEARCH_DEFAULT_INDEX'

KEY_AYR_ROLE = 'ayr_role'
KEY_BAG_S3_URL = 'bag_s3_url'
KEY_BAG_DATA = 'bag_data'


def check_verify_ssl_cert() -> bool:
    """
    Determine if SSL certificate checking should be disabled; intended for
    local testing only when accessing a host via an SSH tunnel (and the host
    name in the certificate doesn't match localhost).

    Disable checking by setting environment variable DO_NOT_VERIFY_SSL to the
    string value TRUE.

    :return: True if SSL cert checking enabled (default), False otherwise.
    """
    try:
        if os.environ[ENV_DO_NOT_VERIFY_SSL] == 'TRUE':
            print(f'check_verify_ssl_cert: do not verify')
            return False
    except KeyError:
        print(f'check_verify_ssl_cert: "{ENV_DO_NOT_VERIFY_SSL}" not set')

    print(f'check_verify_ssl_cert: verify')
    return True


def get_opensearch_user_password() -> str:
    """
    Gets OpenSearch password from AWS ParameterStore; or, for local testing
    only, environment variable OPENSEARCH_USER_PASSWORD. The AWS
    ParameterStore key name is loaded from environment variable
    OPENSEARCH_USER_PASSWORD_PARAM_STORE_KEY.

    :return: String containing OpenSearch password.
    """
    try:
        return os.environ[ENV_OPENSEARCH_USER_PASSWORD]
    except KeyError:
        print(f'Environment variable "{ENV_OPENSEARCH_USER_PASSWORD}" not set')
        print(f'Getting param store key from "{ENV_OPENSEARCH_USER_PASSWORD_PARAM_STORE_KEY}"')
        param_store_key = os.environ[ENV_OPENSEARCH_USER_PASSWORD_PARAM_STORE_KEY]
        print(f'param_store_key={param_store_key}')
        client_ssm = boto3.client('ssm')
        print('Calling client_ssm.get_parameter')
        return client_ssm.get_parameter(
            Name=param_store_key,
            WithDecryption=True
        )['Parameter']['Value']


def get_opensearch_url() -> str:
    """
    Returns base part of OpenSearch host URL from environment variable
    OPENSEARCH_HOST_URL.

    :return: OpenSearch host base URL.
    """
    opensearch_host_url = os.environ[ENV_OPENSEARCH_HOST_URL]
    if not opensearch_host_url.endswith('/'):
        print(f'get_opensearch_url: appending /')
        opensearch_host_url += '/'
    print(f'get_opensearch_url: opensearch_host_url={opensearch_host_url}')
    return opensearch_host_url


def validate_event(event):
    """
    Raise error if event not valid.

    :param event: AWS Lambda event
    """
    if KEY_AYR_ROLE not in event:
        raise AYRBagToOpenSearchError(f'Key "{KEY_AYR_ROLE} not found"')
    if KEY_BAG_S3_URL not in event:
        raise AYRBagToOpenSearchError(f'Key "{KEY_BAG_S3_URL} not found"')
    if KEY_BAG_DATA not in event:
        raise AYRBagToOpenSearchError(f'Key "{KEY_BAG_DATA} not found"')


def lambda_handler(event, context):
    """
    Insert incoming Bag OpenSearch record into OpenSearch.

    Expects the following input event format (e.g. from da-ayr-bag-unpacker):

    {
      "ayr_role": "...",
      "bag_s3_url": "TDR-2022-D6WD.tar.gz",
      "bag_data": {
        "bag-info.txt": {
            ...
        },
        ...
        "bag_sub_files": [
            {
                "object": "ayr-in/TDR-2022-D6WD.tar.gz/TDR-2022-D6WD/data/content/file-c1.txt",
                "data": "dummy data in sample for file-c1.txt"
            },
            ...
        ]
      }
    }

    :param event: AWS Lambda event
    :param context: AWS Lambda context
    :return: AWS Lambda response
    """
    print(f'--- event start {"-" * 64}\n{event}\n--- event end {"-" * 66}')
    print(f'--- context start {"-" * 62}\n{context}\n--- context end {"-" * 64}')
    verify_ssl_cert = check_verify_ssl_cert()
    print(f'verify_ssl_cert={verify_ssl_cert}')
    opensearch_host_url = get_opensearch_url()
    opensearch_user = os.environ[ENV_OPENSEARCH_USER]
    opensearch_user_password = get_opensearch_user_password()
    credentials = (opensearch_user, opensearch_user_password)
    opensearch_index = os.environ[ENV_OPENSEARCH_INDEX]
    print(f'opensearch_index={opensearch_index}')
    opensearch_insert_id = event['bag_data']['bag-info.txt']['Internal-Sender-Identifier']
    url = f'{opensearch_host_url}{opensearch_index}/_doc/{opensearch_insert_id}'
    print(f'url={url}')

    headers = {
        'Content-Type': 'application/json'
    }

    data = json.dumps(event)
    print(f'--- data start {"-" * 65}\n{data}\n--- data end {"-" * 67}')

    response = requests.put(
        url,
        verify=verify_ssl_cert,
        auth=credentials,
        headers=headers,
        data=data
    )

    response.raise_for_status()  # raise error if response not OK
    response_json = response.json()
    print(response_json)

    return {
        'statusCode': 200,
        'body': json.dumps(response_json)
    }
