import boto3
import json
import os
import importlib
from botocore.exceptions import ClientError

from handle_event import * 
from send_events_and_errors import * 

#Feed in the SNS Topic from an env. variable
SNS_TOPIC_ARN = os.getenv('SNS_TOPIC_ARN','')

#Bring the data in and parse the SNS message
def lambda_handler(event, context):
    text_output_array = ["-------------------------\n"]

    ### If events come from SNS, this works. If not, check to see if they came from cloudwatch logs and GuardDuty
    try: # Standard Dome9 event source via SNS
        raw_message = event['Records'][0]['Sns']['Message']
        message = json.loads(raw_message)

        # Check for source. Transform it to "Dome9" format if it's not originating from Dome9. 
        # This expects that GD is triggering lambda via SNS. This is neeeded for running cross-region GD events. 
        if "source" in message and message["source"] == "aws.guardduty": # GuardDuty event source via CW Events
            text_output_array.append("Event Source: GuardDuty\n")
            gd_transform_module = importlib.import_module('transform_gd_event')
            unformatted_message = event["detail"]        
            found_action, text_output, message = gd_transform_module.transform_gd_event(unformatted_message)
            text_output_array.append(text_output)
            if not found_action:
                print(text_output_array)
                return      
    except: 
        print("Unexpected error. Exiting")
        return

    print(message) #log the input for troubleshooting

    timestamp = "ReportTime: " + str(message['reportTime']) + "\n"

    text_output_array.append(timestamp)

    event_account = "Account id: " + message['account']['id'] + "\n"
    text_output_array.append(event_account)

    try:
        text_output_array, post_to_sns = handle_event(message,text_output_array)
    except Exception as e: 
        post_to_sns = True
        text_output_array.append("Handle_event failed\n")
        text_output_array.append(str(e))

    
    if SNS_TOPIC_ARN != '' and post_to_sns:
        sendEvent(text_output_array,SNS_TOPIC_ARN)

    if not SNS_TOPIC_ARN:
        print("SNS topic out was not defined!")

    print(text_output_array)
    return


