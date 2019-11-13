'''
## iam_user_disable_console_password
What it does:
Usage: AUTO: iam_user_disable_console_password
Limitations: none
'''

import boto3
from botocore.exceptions import ClientError


def run_action(boto_session, rule, entity, params):
    username = entity['name']
    iam_client = boto3.client('iam')
    try:
        iam_client.delete_login_profile(UserName=username)
        return f'user: {username} login profile was deleted successfully.'

    except ClientError as e:
        return f'Unexpected error: {e}.'
