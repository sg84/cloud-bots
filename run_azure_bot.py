import os
import json
import sys
sys.path.append('./packages/')

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

    # Loop through Lambda environment variables and pull in all the account keys
    # If we find a variable called azure_key<#>, pull it in and bring in the credentials
    # Check those credentials to see if we have the key for the account we want
    try:
        string_azure_credentials = os.getenv('AZURE_CREDENTIALS','')
        azure_credentials = json.loads(string_azure_credentials)
        for key, value in azure_credentials.items():
            if subscription_id == value['AZURE_SUBSCRIPTION_ID']:
                print("Found credentials for Azure tenant. Running bot.")
                found_credentials = True
                break     
    except:
        text_output = text_output + "Formatting error for key %s \n Please Format like: {\n"subscriptionname1": {\n"AZURE_TENANT_ID": "abcd",\n"AZURE_CLIENT_ID": "efgh",\n"AZURE_CLIENT_SECRET": "ijkl",\n"AZURE_SUBSCRIPTION_ID": "mnop"\n},\n"subscriptionname2": {\n"AZURE_TENANT_ID": "abcd",\n"AZURE_CLIENT_ID": "efgh",\n"AZURE_CLIENT_SECRET": "ijkl",\n"AZURE_SUBSCRIPTION_ID": "mnop"\n}\n }\nExiting\n" % key
        return text_output,post_to_sns,bot_msg

    if found_credentials:        
        try:
            credentials = ServicePrincipalCredentials(
            client_id=value['AZURE_CLIENT_ID'],
            secret=value['AZURE_CLIENT_SECRET'],
            tenant=value['AZURE_TENANT_ID']
            )
        except:
            text_output = text_output + "Formatting error for key %s \n Please Format like: {\n"subscriptionname1": {\n"AZURE_TENANT_ID": "abcd",\n"AZURE_CLIENT_ID": "efgh",\n"AZURE_CLIENT_SECRET": "ijkl",\n"AZURE_SUBSCRIPTION_ID": "mnop"\n},\n"subscriptionname2": {\n"AZURE_TENANT_ID": "abcd",\n"AZURE_CLIENT_ID": "efgh",\n"AZURE_CLIENT_SECRET": "ijkl",\n"AZURE_SUBSCRIPTION_ID": "mnop"\n}\n }\nExiting\n" % key
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
