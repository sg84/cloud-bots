'''
storage_account_require_https
Usage: AUTO: storage_account_require_https
Sample GSL: StorageAccount should have httpsOnlyTraffic=true
'''

import traceback
from packages.msrestazure.azure_exceptions import CloudError

from azure.mgmt.storage.models import StorageAccountUpdateParameters

def run_action(azure_client,rule,entity,params):
  text_output = ""

  resource_group_name = entity['resourceGroup']['name']
  storage_account_name = entity['name']

  try:
    text_output = "Updating setting for enabling HTTPS only traffic on Storage Account: %s \n" % storage_account_name

    # Update storage account
    print('Updating storage account')
    storage_account = azure_client['storage'].storage_accounts.update(
        resource_group_name, 
        storage_account_name,
        StorageAccountUpdateParameters(
            enable_https_traffic_only=True
        )  
    )

  except CloudError:
    text_output =  text_output + 'Operation failed:' + traceback.format_exc()
      
  else:
    text_output = text_output +  "Storage account: %s successfully updated\n" % storage_account_name

  return text_output



