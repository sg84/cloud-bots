import os
import json
import boto3
import sys
sys.path.append('./packages/')

from base64 import b64decode

from packages.azure.common.credentials import ServicePrincipalCredentials
from packages.azure.mgmt.resource import ResourceManagementClient
from packages.azure.mgmt.network import NetworkManagementClient
from packages.azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.storage import StorageManagementClient


def run_azure_bot(message,bot_module,params):
    text_output = ""
    bot_msg = ""
    post_to_sns = True
    found_credentials = False

    subscription_id = message['account']['id']
    text_output = "Azure tenant id: %s \n" % subscription_id
   
    try:
        encrypted_credentials = os.environ['AZURE_CREDENTIALS']
        # Decrypt code should run once and variables stored outside of the function
        # handler so that these are decrypted once per container
        string_azure_credentials = boto3.client('kms').decrypt(CiphertextBlob=b64decode(encrypted_credentials))['Plaintext']
        azure_credentials = json.loads(string_azure_credentials)
        for key, value in azure_credentials.items():
            if subscription_id == value['AZURE_SUBSCRIPTION_ID']:
                print("Found credentials for Azure tenant. Running bot.")
                found_credentials = True
                break    
    except:
        text_output = text_output + "Credentials formatting error while scanning for %s credentials\nExiting\n" % subscription_id
        return text_output,post_to_sns,bot_msg

    if found_credentials:        
        try:
            credentials = ServicePrincipalCredentials(
            client_id=value['AZURE_CLIENT_ID'],
            secret=value['AZURE_CLIENT_SECRET'],
            tenant=value['AZURE_TENANT_ID']
            )
        except:
            text_output = text_output + "Credentials formatting error while setting up %s credentials\nExiting\n" % subscription_id
            return text_output,post_to_sns,bot_msg

        azure_client = {}
        azure_client['resource'] = ResourceManagementClient(credentials, subscription_id)
        azure_client['compute'] = ComputeManagementClient(credentials, subscription_id)
        azure_client['network'] = NetworkManagementClient(credentials, subscription_id)
        azure_client['storage'] = StorageManagementClient(credentials, subscription_id)
                    
        ## Run the bot
        bot_msg = bot_module.run_action(azure_client,message['rule'],message['entity'],params)

    else:
        text_output = text_output + "No Azure credentials were found for this tenant. Exiting.\n" 

    return text_output,post_to_sns,bot_msg
