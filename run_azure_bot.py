import sys
sys.path.append('./packages/')

from packages.azure.common.credentials import ServicePrincipalCredentials
from packages.azure.mgmt.resource import ResourceManagementClient
from packages.azure.mgmt.network import NetworkManagementClient
from packages.azure.mgmt.compute import ComputeManagementClient

def run_azure_bot(message,bot_module,params):
    text_output = ""
    post_to_sns = True

    AZURE_TENANT_ID = "ddd5df49-0f38-4bfe-9be9-644b9fd630cf"
    AZURE_CLIENT_ID = "20ab9245-03cb-4336-80d4-2853e13160a5"
    AZURE_CLIENT_SECRET = "E3blJpjc3UR8oZ4PLOv8jt/FqieK5d+Y/KG/Fu0wnJg="
    AZURE_SUBSCRIPTION_ID = "057f8ae2-2a3f-4428-a903-7c5610b0e056"

    subscription_id = AZURE_SUBSCRIPTION_ID
    credentials = ServicePrincipalCredentials(
        client_id=AZURE_CLIENT_ID,
        secret=AZURE_CLIENT_SECRET,
        tenant=AZURE_TENANT_ID
    )

    azure_client = {}
    azure_client['resource'] = ResourceManagementClient(credentials, subscription_id)
    azure_client['compute'] = ComputeManagementClient(credentials, subscription_id)
    azure_client['network'] = NetworkManagementClient(credentials, subscription_id)
    
    ## Run the bot
    bot_msg = bot_module.run_action(azure_client,message['rule'],message['entity'],params)

    return text_output,post_to_sns,bot_msg

