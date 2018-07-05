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
            "entity": {
                "region": unformatted_message["region"]
            }
        }
        # Guard Duty has 2 types of resource events - instance and accesskey. We'll conditionally format the message based on the message type
        # Sample resource information is at the bottom of the file
        if unformatted_message["resource"]["resourceType"] == "Instance":
            formatted_message["entity"]["id"] = unformatted_message["resource"]["instanceDetails"]["instanceId"]
            formatted_message["entity"]["vpc"] = {"id": unformatted_message["resource"]["instanceDetails"]["networkInterfaces"][0]["vpcId"]}

            for tag in unformatted_message["resource"]["instanceDetails"]["tags"]:
                if tag["key"] == "name":
                    formatted_message["entity"]["name"] = tag["value"]
                    break                 
            if "name" not in formatted_message["entity"]:
                formatted_message["entity"]["name"] = ""

        elif unformatted_message["resource"]["resourceType"] == "AccessKey":
            formatted_message["entity"]["id"] = unformatted_message["resource"]["accessKeyId"]
            formatted_message["entity"]["name"] = unformatted_message["resource"]["userName"]

        else:
            text_output = "Unknown resource type found: %s. Current known resources are AccessKeys and Instance. Skipping.\n" % unformatted_message["resource"]["resourceType"]
            found_action = False
            return found_action, text_output, formatted_message


        text_output = text_output + "Successfully formatted GuardDuty finding and found a corresponding bot\n" 
    
    except Exception as e:
        text_output = text_output + "Unexpected error: %s. Exiting\n" % e

    return found_action, text_output, formatted_message



'''
Sample available resource properties for Instance:
"resource": {
    "resourceType": "Instance",
    "instanceDetails": {
    "instanceId": "i-07711445ed3ea4d78",
    "instanceType": "t2.micro",
    "launchTime": "2018-06-21T08:51:00Z",
    "platform": "windows",
    "productCodes": [],
    "networkInterfaces": [
        {
        "networkInterfaceId": "eni-6037c07b",
        "privateIpAddresses": [
            {
            "privateDnsName": "ip-172-31-1-168.us-west-2.compute.internal",
            "privateIpAddress": "172.31.1.168"
            }
        ],
        "subnetId": "subnet-2186c67b",
        "vpcId": "vpc-eab7a493",
        "privateDnsName": "ip-172-31-1-168.us-west-2.compute.internal",
        "securityGroups": [
            {
            "groupName": "windows-bastion",
            "groupId": "sg-2f55695e"
            }
        ],
        "publicIp": "34.217.53.186",
        "ipv6Addresses": [],
        "publicDnsName": "ec2-34-217-53-186.us-west-2.compute.amazonaws.com",
        "privateIpAddress": "172.31.1.168"
        }
    ],
    "tags": [
        {
        "value": "windows-bastion",
        "key": "Name"
        }
    ],
    "instanceState": "running",
    "availabilityZone": "us-west-2c",
    "imageId": "ami-3703414f",
    "imageDescription": "Microsoft Windows Server 2016 with Desktop Experience Locale English AMI provided by Amazon"
    }
}




Sample resource properties for AccessKey:
    "resource": {
    "resourceType": "AccessKey",
    "accessKeyDetails": {
        "accessKeyId": "GeneratedFindingAccessKeyId",
        "principalId": "GeneratedFindingPrincipalId",
        "userType": "IAMUser",
        "userName": "GeneratedFindingUserName"
    }
'''