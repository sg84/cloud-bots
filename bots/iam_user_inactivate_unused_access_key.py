'''
## iam_user_inactivate_unused_access_key
What it does: inactivate unused access key that haven't been in use for some time
Usage: AUTO: iam_user_inactivate_unused_access_key <number of days>
Examples:  AUTO: iam_user_inactivate_unused_access_key 90
Limitations: default time is 90 days, if there are more then 200 access keys for user should increase maxItems
'''

import boto3
from botocore.exceptions import ClientError
MAX_ITEMS = 200

def run_action(boto_session, rule, entity, params):
    text_output = 'Start iam_user_inactivate_unused_access_key'
    username = entity['name']
    max_unused_time = params[0] if params else 90
    iam_client = boto3.client('iam')
    try:
        access_keys = iam_client.list_access_keys(UserName=username, MaxItems=MAX_ITEMS)['AccessKeyMetadata']

        for access_key in access_keys:
            access_key_id = access_key['AccessKeyId']
            access_key_last_use = iam_client.get_access_key_last_used(AccessKeyId=access_key_id)['AccessKeyLastUsed']
            last_used_date = access_key_last_use['LastUsedDate'] - access_key['CreateDate']

            if (last_used_date.days > max_unused_time):
                iam_client.update_access_key(
                    UserName=username,
                    AccessKeyId=access_key_id,
                    Status='Inactive'
                )
                text_output = text_output + f'Iam user: {username} access key with id : {access_key_id} was deactivated'

    except ClientError as e:
        text_output = text_output + f'Unexpected error: {e}.'

    return text_output
