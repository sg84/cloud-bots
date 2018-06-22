import boto3
import os

account_mode = os.getenv('ACCOUNT_MODE','')
cross_account_role_name = os.getenv('CROSS_ACCOUNT_ROLE_NAME','')

def run_aws_bot(message,bot_module,params):
    #Initial setup
    region = message['entity']['region']
        
    # Some events come through with 'null' as the region. If so, default to us-east-1
    if region == None or region == "":
        region = 'us-east-1'        
    else:
        region = region.replace("_","-")

    post_to_sns = True
    bot_msg = ""
    text_output = ""
    
    # Get the session info here. No point in waisting cycles running it up top if we aren't going to run an bot anyways:
    try:
        #get the accountID
        sts = boto3.client("sts")
        lambda_account_id = sts.get_caller_identity()["Account"]

    except ClientError as e:
        text_output = "Unexpected STS error: %s \n"  % e
        return text_output,post_to_sns,bot_msg                     

    #Make sure that the event that's being referenced is for the account this function is running in.
    event_account_id = message['account']['id']

    #Account mode will be set in the lambda variables. We'll default to single mdoe               
    if lambda_account_id != event_account_id: #The remediation needs to be done outside of this account

        if account_mode == "multi": #multi or single account mode?
                #If it's not the same account, try to assume role to the new one
                if cross_account_role_name: # This allows users to set their own role name if they have a different naming convention they have to follow
                    role_arn = "arn:aws:iam::" + event_account_id + ":role/" + cross_account_role_name
                else:
                    role_arn = "arn:aws:iam::" + event_account_id + ":role/Dome9CloudBots"

                text_output = "Compliance failure was found for an account outside of the one the function is running in. Trying to assume_role to target account %s .\n" % event_account_id

                # create an STS client object that represents a live connection to the STS service
                sts_client = boto3.client('sts')
                
                # Call the assume_role method of the STSConnection object and pass the role ARN and a role session name.
                try:
                    assumedRoleObject = sts_client.assume_role(
                        RoleArn=role_arn,
                        RoleSessionName="CloudBotsAutoRemedation"
                        )
                    # From the response that contains the assumed role, get the temporary credentials that can be used to make subsequent API calls
                    credentials_for_event = assumedRoleObject['Credentials']

                except ClientError as e:
                    error = e.response['Error']['Code']
                    print(e)
                    if error == 'AccessDenied':
                        text_output = text_output + "Tried and failed to assume a role in the target account. Please verify that the cross account role is createad. \n"
                    else:
                        text_output = text_output +  "Unexpected error: %s \n" % e
                        bot_msg = ""
                        return text_output,post_to_sns,bot_msg                     

                boto_session = boto3.Session(
                    region_name=region,         
                    aws_access_key_id = credentials_for_event['AccessKeyId'],
                    aws_secret_access_key = credentials_for_event['SecretAccessKey'],
                    aws_session_token = credentials_for_event['SessionToken']
                )

        else:
            # In single account mode, we don't want to try to run bots outside of this one
            text_output = "Error: This finding was found in account id %s. The Lambda function is running in account id: %s. Remediations need to be ran from the account there is the issue in.\n" % (event_account_id, lambda_account_id)
            post_to_sns = False

            return text_output,post_to_sns,bot_msg

    else:
        #Boto will default to default session if we don't need assume_role credentials
        boto_session = boto3.Session(region_name=region)                     

    ## Run the bot
    bot_msg = bot_module.run_action(boto_session,message['rule'],message['entity'],params)

    return text_output,post_to_sns,bot_msg