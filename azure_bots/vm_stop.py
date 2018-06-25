'''
azure_stop_vm
Usage: AUTO: azure_stop_vm

'''

import traceback
from packages.msrestazure.azure_exceptions import CloudError

def run_action(azure_client,rule,entity,params):
  text_output = ""

  LOCATION = entity['region']
  GROUP_NAME = entity['resourceGroup']['name']
  VM_NAME = entity['name']

  try:
      text_output = "Trying to turn off VM: %s \n" % VM_NAME

      async_vm_stop = azure_client['compute'].virtual_machines.power_off(GROUP_NAME, VM_NAME)
      async_vm_stop.wait()

  except CloudError:
      text_output =  text_output + 'A VM operation failed:' + traceback.format_exc()
      
  else:
      text_output = text_output +  "VM: %s successfully turned off\n" % VM_NAME

  return text_output
