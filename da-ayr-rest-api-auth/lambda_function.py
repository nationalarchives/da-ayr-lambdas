import boto3
import os
import requests

ENV_PARAM_STORE_KEY_KEYCLOAK_CLIENT_SECRET = 'PARAM_STORE_KEY_KEYCLOAK_CLIENT_SECRET'
ENV_KEYCLOAK_HOST = 'KEYCLOAK_HOST'
ENV_KEYCLOAK_CLIENT_ID = 'KEYCLOAK_CLIENT_ID'
ENV_KEYCLOAK_REALM = 'KEYCLOAK_REALM'
client_ssm = boto3.client('ssm')


def get_parameter_store_key_value(key: str, encrypted=True) -> str:
    """
    Get string value of `key` in Parameter Store.

    :param key: Name of key whose value will be returned.
    :param encrypted: Whether key is encrypted (boolean).
    :return: String value of requested Parameter Store key.
    """
    print(f'get_parameter_store_key_value: key="{key}"')
    return client_ssm.get_parameter(
        Name=key,
        WithDecryption=encrypted
    )['Parameter']['Value']


def get_keycloak_token_introspect_response(token: str):
    print(f'get_keycloak_token_introspect_response: token={token}')
    key_keycloak_secret = os.environ[ENV_PARAM_STORE_KEY_KEYCLOAK_CLIENT_SECRET]
    print(f'get_keycloak_token_introspect_response: key_keycloak_secret={key_keycloak_secret}')
    keycloak_client_secret = get_parameter_store_key_value(key_keycloak_secret)
    keycloak_host = os.environ[ENV_KEYCLOAK_HOST]
    print(f'get_keycloak_token_introspect_response: keycloak_host={keycloak_host}')
    keycloak_client_id = os.environ[ENV_KEYCLOAK_CLIENT_ID]
    print(f'get_keycloak_token_introspect_response: keycloak_client_id={keycloak_client_id}')
    keycloak_realm = os.environ[ENV_KEYCLOAK_REALM]
    print(f'get_keycloak_token_introspect_response: keycloak_realm={keycloak_realm}')

    url = (
        f'https://{keycloak_host}/realms/{keycloak_realm}'
        '/protocol/openid-connect/token/introspect'
    )

    print(f'get_keycloak_token_introspect_response: url={url}')

    verify_ssl_cert = True
    headers = {}
    data = {
        'client_id': keycloak_client_id,
        'client_secret': keycloak_client_secret,
        'token': token
    }

    response = requests.post(
        url,
        verify=verify_ssl_cert,
        headers=headers,
        data=data
    )

    print(f'response={response}')
    response.raise_for_status()  # raise error if response not OK
    print(f'response.content={response.content}')
    print(f'response.json()={response.json()}')

    return response.json()


def lambda_handler(event, context):
    print(f'event:\n{event}')
    method_arn = event['methodArn']
    print(f'method_arn={method_arn}')
    method_arn_parts = method_arn.split(':')
    api_name = method_arn_parts[2]
    print(f'api_name={api_name}')
    aws_region = method_arn_parts[3]
    print(f'aws_region={aws_region}')
    aws_account_id = method_arn_parts[4]
    print(f'aws_account_id={aws_account_id}')
    arn_end_parts = method_arn_parts[5].split('/')
    print(f'api_gateway_arn={arn_end_parts}')
    rest_api_id = arn_end_parts[0]
    stage = arn_end_parts[1]

    # Check Keycloak token
    keycloak_response = get_keycloak_token_introspect_response(
        event['authorizationToken']
    )

    print(f'keycloak_response={keycloak_response}')
    print(f'type(keycloak_response)={type(keycloak_response)}')

    # Only Allow if 'active' key in Keycloak token check response is true
    effect = 'Allow' if keycloak_response['active'] is True else 'Deny'

    auth_response = {
        'principalId': None,
        'policyDocument': {
            'Version': '2012-10-17',
            'Statement': [
                {
                    'Action': f'{api_name}:Invoke',
                    'Effect': effect,
                    'Resource': [
                        f'arn:aws:{api_name}:{aws_region}:{aws_account_id}:{rest_api_id}/{stage}/*/*'
                    ]
                }
            ]
        }
    }

    print(f'auth_response:\n{auth_response}')
    return auth_response
