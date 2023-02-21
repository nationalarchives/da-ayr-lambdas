import json
import os
import requests
import boto3

ENV_DO_NOT_VERIFY_SSL = 'DO_NOT_VERIFY_SSL'  # e.g. set to TRUE for local testing via ssh tunnel
ENV_OPENSEARCH_HOST_URL = 'OPENSEARCH_HOST_URL'
ENV_OPENSEARCH_INDEX = 'OPENSEARCH_INDEX'  # Can set here or in POST payload
ENV_OPENSEARCH_USER = 'OPENSEARCH_USER'
ENV_OPENSEARCH_USER_PASSWORD = 'OPENSEARCH_USER_PASSWORD'  # local testing only
ENV_OPENSEARCH_USER_PASSWORD_PARAM_STORE_KEY = 'OPENSEARCH_USER_PASSWORD_PARAM_STORE_KEY'
ENV_OPENSEARCH_DEFAULT_INDEX = 'OPENSEARCH_DEFAULT_INDEX'
JSON_KEY_BODY = 'body'
JSON_KEY_OPENSEARCH_INDEX = 'opensearch_index'
JSON_KEY_SOURCE_ORG = 'Source-Organization'


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


def get_opensearch_index(event) -> str:
    """
    Return the OpenSearch index to use; uses value in environment variable
    OPENSEARCH_INDEX if present, otherwise value from event payload, or an
    empty string if no value is set.
    :param event: AWS Lambda event
    :return: OpenSearch index name to be used; can be empty.
    """
    try:
        return os.environ[ENV_OPENSEARCH_INDEX]
    except KeyError:
        print(f'get_opensearch_index: env var "{ENV_OPENSEARCH_DEFAULT_INDEX}" not set')
        if JSON_KEY_OPENSEARCH_INDEX in event:
            # Lambda with payload at top level
            print(f'get_opensearch_index: found key {JSON_KEY_OPENSEARCH_INDEX}')
            return event[JSON_KEY_OPENSEARCH_INDEX]
        elif JSON_KEY_BODY in event:
            # Lambda with payload in body key
            print(f'get_opensearch_index: found key {JSON_KEY_BODY}')
            body = json.loads(event['body'])
            if JSON_KEY_OPENSEARCH_INDEX in body:
                print(f'get_opensearch_index: found key {JSON_KEY_OPENSEARCH_INDEX}')
                return body[JSON_KEY_OPENSEARCH_INDEX]
        print(f'get_opensearch_index: no index given')
        return ''


def get_event_key(event, key: str) -> str:
    """
    Returns `key` value from event; either at top-level, or in `body` key;
    returns empty string if not found.
    :param event: Lambda event
    :param key: Name of key whose value is to be returned
    :return: Key value
    """
    if key in event:
        # Lambda with payload at top level
        print(f'get_event_key: found key "{key}" at top level')
        return event[key]
    elif JSON_KEY_BODY in event:
        # Lambda with payload in body key
        print(f'get_event_key: found key {JSON_KEY_BODY}')
        body = json.loads(event['body'])
        if key in body:
            print(f'get_event_key: found key {key} in {JSON_KEY_BODY}')
            return body[key]
    return ''


def lambda_handler(event, context):
    """
    Handler to run a query against an OpenSearch host.

    :param event: AWS Lambda event
    :param context: AWS Lambda context
    :return: AWS Lambda response
    """
    print(f'--- event start {"-" * 64}\n{event}\n--- event end {"-" * 66}')
    print(f'--- context start {"-" * 62}\n{context}\n--- context end {"-" * 64}')
    verify_ssl_cert = check_verify_ssl_cert()
    opensearch_host_url = get_opensearch_url()
    opensearch_user = os.environ[ENV_OPENSEARCH_USER]
    opensearch_user_password = get_opensearch_user_password()
    credentials = (opensearch_user, opensearch_user_password)
    opensearch_index = get_opensearch_index(event)
    print(f'opensearch_index={opensearch_index}')
    if len(opensearch_index) > 0:
        opensearch_index += '/'
    url = opensearch_host_url + f'{opensearch_index}_search?pretty=true'
    print(f'url={url}')
    source_organization = get_event_key(event=event, key=JSON_KEY_SOURCE_ORG)
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
