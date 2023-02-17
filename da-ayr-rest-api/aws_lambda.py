import json
import os
import requests
import boto3

ENV_DO_NOT_VERIFY_SSL = 'DO_NOT_VERIFY_SSL'  # e.g. set to TRUE for local testing via ssh tunnel
ENV_OPENSEARCH_HOST_URL = 'OPENSEARCH_HOST_URL'
ENV_OPENSEARCH_USER = 'OPENSEARCH_USER'
ENV_OPENSEARCH_USER_PASSWORD = 'OPENSEARCH_USER_PASSWORD'  # local testing only
ENV_OPENSEARCH_USER_PASSWORD_PARAM_STORE_KEY = 'OPENSEARCH_USER_PASSWORD_PARAM_STORE_KEY'


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


def get_opensearch_query(source_organization: str) -> str:
    """
    Builds an example OpenSearch query.

    :param source_organization:
    :return: JSON formatted OpenSearch example query.
    """
    return json.dumps(
        {
            "query": {
                "match_phrase": {
                    "Source-Organization": source_organization
                }
            }
        }
    )


def lambda_handler(event, context):
    """
    Handler to run a query against an OpenSearch host.

    :param event: AWS Lambda event
    :param context: AWS Lambda context
    :return: AWS Lambda response
    """
    print(f'--- event {"-" * 70}\n{event}')
    print(f'--- context {"-" * 68}\n{context}')
    verify_ssl_cert = check_verify_ssl_cert()
    opensearch_host_url = get_opensearch_url()
    opensearch_user = os.environ[ENV_OPENSEARCH_USER]
    opensearch_user_password = get_opensearch_user_password()
    credentials = (opensearch_user, opensearch_user_password)
    opensearch_index = json.loads(event['body'])['opensearch_index']
    print(f'opensearch_index={opensearch_index}')
    url = opensearch_host_url + f'{opensearch_index}/_search?pretty=true'
    print(f'url={url}')
    source_organization = json.loads(event['body'])['Source-Organization']
    print(f'source_organization={source_organization}')
    opensearch_query_json = get_opensearch_query(source_organization)

    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.post(
        url,
        verify=verify_ssl_cert,
        auth=credentials,
        headers=headers,
        data=opensearch_query_json
    )

    response.raise_for_status()  # raise error if response not OK
    response_json = response.json()
    print(response_json)

    return {
        'statusCode': 200,
        'body': json.dumps(response_json)
    }
