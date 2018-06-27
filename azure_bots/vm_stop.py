'''
vm_stop
Usage: AUTO: vm_stop
'''

import traceback
from packages.msrestazure.azure_exceptions import CloudError

def run_action(azure_client,rule,entity,params):
  text_output = ""

  resource_group_name = entity['resourceGroup']['name']
  vm_name = entity['name']

  try:
    text_output = "Trying to turn off VM: %s \n" % vm_name

    async_vm_stop = azure_client['compute'].virtual_machines.power_off(resource_group_name, vm_name)
    async_vm_stop.wait()

  except CloudError:
    text_output =  text_output + 'A VM operation failed:' + traceback.format_exc()
      
  else:
    text_output = text_output +  "VM: %s successfully turned off\n" % vm_name

  return text_output
