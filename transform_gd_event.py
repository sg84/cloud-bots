'''
Sample required minimum event structure that we're formatting the event to:

{
  "reportTime": "2018-03-20T05:40:42.043Z",
  "rule": {
    "name": "Instance should fail",
    "complianceTags": "AUTO: tag_ec2_resource myKey myValue"
  },
  "status": "Failed",
  "account": {
    "id": "621958466464"
  },
  "entity": {
    "id": "i-0028f9751d334c93a",
    "name": "TestInstance",
    "region": "us_west_2"
  }
}

'''
import json
import os

def transform_gd_event(unformatted_message):
    found_action = False
    formatted_message = ""
    text_output = ""

    #Check the OS variables to get the list of what we want to do for the different GD actions
    try:
        gd_actions = json.loads(os.environ['GD_ACTIONS'])
        for gd_finding_type, action in gd_actions.items():
            if unformatted_message["type"] == gd_finding_type and "AUTO:" in action["bot"]:
                text_output = "Found a defined rule for GD finding %s. Continuing\n" % gd_finding_type
                found_action = True
                break    

    except Exception as e:
        text_output = "Unexpected error %s \n Please check the formatting of the GD_ACTIONS env variable in Lambda\n Exiting\n" % e
        return found_action, text_output, formatted_message
    
    if not found_action:
        text_output = "GuardDuty event found but no bots were defined for the event %s. Skipping\n" % unformatted_message["type"] 
        return found_action, text_output, formatted_message

    try:
        # Make the main structure of the formatted message
        formatted_message = {
            "reportTime": unformatted_message["createdAt"],
            "rule": {
                "name": action["name"],
                "complianceTags": action["bot"]
            },
            "status": "Failed",
            "account": {
                "id": unformatted_message["accountId"],
                "vendor": "Aws"
            },
            "entity": {}
        }

        ## Build out ifs for different resource types and add those into the formatted_message
        if unformatted_message["resource"]["resourceType"] == "Instance":
            formatted_message["entity"]["id"] = unformatted_message["resource"]["instanceDetails"]["instanceId"]
            
            formatted_message["entity"]["name"] = "" #unformatted_message["instanceDetails"]["tags"] ## Need to add in check for name tag. Leaving blank for now. 
            formatted_message["entity"]["region"] = unformatted_message["region"]

        text_output = text_output + "Successfully formatted GuardDuty finding and found a corresponding bot\n" 
    
    except Exception as e:
        text_output = text_output + "Unexpected error: %s. Exiting\n" % e

    return found_action, text_output, formatted_message
