import re
import boto3
import importlib 
# from run_aws_bot import *
# from run_azure_bot import *

from botocore.exceptions import ClientError

def handle_event(message,text_output_array):
    post_to_sns = True
    #Break out the values from the JSON payload from Dome9
    rule_name = message['rule']['name']
    status = message['status']
    entity_name = message['entity']['name']
    cloud_provider = message['account']['vendor']
    if cloud_provider == "Aws":
        entity_id = message['entity']['id']
    else: ######### Azure IDs are nested in a resource group but I'm not sure if every event comes through with an RG. Ignoring the ID for now and adding in error handling later
        entity_id = ""
    

    #All of the remediation values are coming in on the compliance tags and they're pipe delimited
    compliance_tags = message['rule']['complianceTags'].split("|")



    #evaluate the event and tags and decide is there's something to do with them. 
    if status == "Passed":
        text_output_array.append("Previously failing rule has been resolved: %s \n ID: %s \nName: %s \n" % (rule_name, entity_id, entity_name))
        post_to_sns = False
        return text_output_array,post_to_sns

    #Check if any of the tags have AUTO: in them. If there's nothing to do at all, skip it. 
    auto_pattern = re.compile("AUTO:")
    if not auto_pattern.search(message['rule']['complianceTags']):
        text_output_array.append("Rule %s \n Doesn't have any 'AUTO:' tags. \nSkipping.\n" % rule_name)
        post_to_sns = False
        return text_output_array,post_to_sns

    for tag in compliance_tags:
        tag = tag.strip() #Sometimes the tags come through with trailing or leading spaces. 

        #Check the tag to see if we have AUTO: in it
        pattern = re.compile("^AUTO:\s.+")
        if pattern.match(tag):
            text_output_array.append("Rule violation found: %s \nID: %s | Name: %s \nCloud: %s \nRemediation bot: %s \n" % (rule_name, entity_id, entity_name, cloud_provider, tag))

            # Pull out only the bot verb to run as a function
            # The format is AUTO: bot_name param1 param2
            arr = tag.split(' ')
            if len(arr) < 2:
                err_msg = "Empty AUTO: tag. No bot was specified"
                print(err_msg)
                text_output_array.append(err_msg)
                continue
            
            bot = arr[1]
            params = arr[2:]

            try:
                if cloud_provider == "Aws":
                    aws_bot = importlib.import_module('run_aws_bot')
                    bot_module = importlib.import_module('aws_bots.' + bot, package=None)
                elif cloud_provider == "Azure":
                    azure_bot = importlib.import_module('run_azure_bot')
                    bot_module = importlib.import_module('azure_bots.' + bot, package=None)
                else:
                    return ("Event found outside of AWS or Azure. Skipping")    

            except:
                print("Error: could not find bot: " + bot)
                text_output_array.append("Bot: %s is not a known bot. Skipping.\n" % bot)
                continue
            
            print("Found bot '%s', about to invoke it" % bot)

            try:
                if cloud_provider == "Aws":
                   text_output, post_to_sns, bot_msg = aws_bot.run_aws_bot(message,bot_module,params)
                   text_output_array.append(text_output)
                elif cloud_provider == "Azure":
                   text_output, post_to_sns, bot_msg = azure_bot.run_azure_bot(message,bot_module,params)
                   text_output_array.append(text_output)


            except Exception as e: 
                bot_msg = "Error while executing function '%s'.\n Error: %s \n" % (bot,e)
                print(bot_msg)
            finally:
                text_output_array.append(bot_msg)

    #After the remediation functions finish, send the notification out. 
    return text_output_array,post_to_sns
