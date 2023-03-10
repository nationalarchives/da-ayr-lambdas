import os
import boto3
import json


class AYRBagRoleAssignerError(Exception):
    """
    For Lambda errors.
    """


ENV_AYR_ROLE_MAP = 'AYR_ROLE_MAP'  # local testing only
ENV_AYR_ROLE_MAP_PARAM_STORE_KEY = 'AYR_ROLE_MAP_PARAM_STORE_KEY'

KEY_AYR_ROLE = 'ayr_role'
KEY_BAG_S3_URL = 'bag_s3_url'
KEY_BAG_DATA = 'bag_data'

KEY_ROLE_MAP_BAG_DEPARTMENT = 'bag_department'
KEY_ROLE_MAP_AYR_ROLE = 'ayr_role'


def get_ayr_role_map_list() -> list:
    """
    Gets AYR role map list from AWS ParameterStore; or, for local testing,
    environment variable AYR_ROLE_MAP. The AWS ParameterStore key name is
    loaded from environment variable AYR_ROLE_MAP_PARAM_STORE_KEY.

    :return: List of AYR department to role mappings.
    """
    try:
        return json.loads(os.environ[ENV_AYR_ROLE_MAP])
    except KeyError:
        print(f'Environment variable "{ENV_AYR_ROLE_MAP}" not set')
        print(f'Getting param store key from "{ENV_AYR_ROLE_MAP_PARAM_STORE_KEY}"')
        param_store_key = os.environ[ENV_AYR_ROLE_MAP_PARAM_STORE_KEY]
        print(f'param_store_key={param_store_key}')
        client_ssm = boto3.client('ssm')
        print('Calling client_ssm.get_parameter')
        return json.loads(
            client_ssm.get_parameter(
                Name=param_store_key,
                WithDecryption=True
            )['Parameter']['Value']
        )


def validate_event(event):
    """
    Raise error if event not valid.

    :param event: AWS Lambda event
    """
    if KEY_AYR_ROLE not in event:
        raise AYRBagRoleAssignerError(f'Key "{KEY_AYR_ROLE} not found"')
    if KEY_BAG_S3_URL not in event:
        raise AYRBagRoleAssignerError(f'Key "{KEY_BAG_S3_URL} not found"')
    if KEY_BAG_DATA not in event:
        raise AYRBagRoleAssignerError(f'Key "{KEY_BAG_DATA} not found"')


def get_ayr_role(department: str) -> str:
    print(f'get_ayr_role: department={department}')
    role_map_list = get_ayr_role_map_list()
    print(f'role_map_list:\n{role_map_list}')
    for role_map in role_map_list:
        bag_department = str(role_map[KEY_ROLE_MAP_BAG_DEPARTMENT]).strip()
        if bag_department == department:
            return str(role_map[KEY_ROLE_MAP_AYR_ROLE]).strip()

    raise AYRBagRoleAssignerError(
        f'Bag department "{department}" is not mapped to an AYR role; add '
        f'a corresponding mapping record to parameter "'
        f'{os.environ[ENV_AYR_ROLE_MAP_PARAM_STORE_KEY]}" in AWS Parameter '
        f'Store (or, if used, env var "{ENV_AYR_ROLE_MAP}")'
    )


def lambda_handler(event, context):
    """
    Sets the `ayr_role` key in the incoming `event` parameter according to the
    record's department and returns the updated `event` as output.

    Expects the following input event format (e.g. from da-ayr-bag-indexer):

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

    Maps incoming Bag's `Source-Organization` to an `ayr_role` name using a
    lookup list. The lookup list is sourced from a Parameter Store key
    specified by env var AYR_ROLE_MAP_PARAM_STORE_KEY (alternatively, for
    testing, the list can be stored in env var AYR_ROLE_MAP). The lookup list
    format must be as follows:

    [
        {
            "bag_department": "Testing A",
            "ayr_role": "department_a_role"
        },
        ...
    ]

    :param event: AWS Lambda event
    :param context: AWS Lambda context
    :return: AWS Lambda response
    """
    print(f'--- event start {"-" * 64}\n{event}\n--- event end {"-" * 66}')
    print(f'--- context start {"-" * 62}\n{context}\n--- context end {"-" * 64}')
    validate_event(event)
    source_organization = event['bag_data']['bag-info.txt']['Source-Organization']
    print(f'source_organization={source_organization}')
    event['ayr_role'] = get_ayr_role(department=source_organization)
    return event
