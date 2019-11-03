import json
from handle_event import *
from send_events_and_errors import *
from send_logs import *
import time


# Feed in the SNS Topic from an env. variable
SNS_TOPIC_ARN = os.getenv('SNS_TOPIC_ARN', '')

# Bring the data in and parse the SNS message
def lambda_handler(event, context):
    start_time = time.time()
    output_message = {}
    source_message = {
  "status": "Failed",
  "policy": {
    "name": "FindingsToRemediation",
    "description": ""
  },
  "findingKey": "lJYwtXfpqyy/pkIoshzAnA",
  "bundle": {
    "name": "Amdocs- P1 Tests",
    "description": "P1 TESTS",
    "id": 90701
  },
  "reportTime": "2019-10-29T13:04:51.546Z",
  "rule": {
    "name": "Ensure no security groups allow ingress from 0.0.0.0/0 to SSH (TCP:22)",
    "ruleId": "",
    "description": "Security groups provide stateful filtering of ingress/egress network traffic to AWS resources. It is recommended that no security group allows unrestricted ingress access to port 22.",
    "remediation": "Removing unfettered connectivity to remote console services, such as SSH, reduces a server's exposure to risk. \n\n1. Login to the AWS Management Console at https://console.aws.amazon.com/vpc/home \n2. In the left pane, click Security Groups \n3. For each security group, perform the following: \n4. Select the security group \n5. Click the Inbound Rules tab \n6. Identify the rules to be removed \n7. Click the x in the Remove column \n8. Click Save \n\nFor additional guidance, refer to control 4.1 in the CIS Amazon Web Services Foundations Benchmark v1.1.0 document that can be downloaded from: https://downloads.cisecurity.org/#/all \n\nAdditional Reference: \nCIS Amazon Web Services Foundations Benchmark v1.1.2 \nhttps://d0.awsstatic.com/whitepapers/compliance/AWS_CIS_Foundations_Benchmark.pdf",
    "complianceTags": "AUTO: sg_split_all_traffic_by_ports 22 3389|AUTO: sg_single_rule_delete split=false protocol=TCP scope=0.0.0.0/0 direction=inbound port=22",
    "logicHash": "4gQXr/FUdkD3nfc0k2HekQ",
    "severity": "High"
  },
  "account": {
    "id": "960952821882",
    "name": "dome9-playground-0000070",
    "vendor": "AWS",
    "dome9CloudAccountId": "33af7241-b8bb-453d-a3da-19c2803388e9"
  },
  "region": "Ohio",
  "entity": {
    "description": "split_test",
    "inboundRules": [
      {
        "protocol": "TCP",
        "port": 0,
        "portTo": 65535,
        "scope": "0.0.0.0/0",
        "scopeMetaData": "null",
        "serviceType": "CIDR"
      },
      {
        "protocol": "tcp",
        "port": 0,
        "portTo": 65535,
        "scope": "::/0",
        "scopeMetaData": "null",
        "serviceType": "CIDR"
      }
    ],
    "outboundRules": [
      {
        "protocol": "ALL",
        "port": 0,
        "portTo": 0,
        "scope": "0.0.0.0/0",
        "scopeMetaData": "null",
        "serviceType": "CIDR"
      },
      {
        "protocol": "ALL",
        "port": 0,
        "portTo": 65535,
        "scope": "0.0.0.0/0",
        "scopeMetaData": "null",
        "serviceType": "CIDR"
      }
    ],
    "inboundPrefixes": [],
    "outboundPrefixes": [],
    "dependentSecurityGroups": "null",
    "networkAssetsStats": [
      {
        "type": "ELBs",
        "count": 0
      },
      {
        "type": "instances",
        "count": 0
      },
      {
        "type": "RDSs",
        "count": 0
      },
      {
        "type": "LambdaFunctions",
        "count": 0
      },
      {
        "type": "Redshifts",
        "count": 0
      },
      {
        "type": "ApplicationLoadBalancers",
        "count": 0
      },
      {
        "type": "EFSs",
        "count": 0
      },
      {
        "type": "ElastiCacheClusters",
        "count": 0
      }
    ],
    "isProtected": "false",
    "networkInterfaces": [],
    "vpc": {
      "cloudAccountId": "33af7241-b8bb-453d-a3da-19c2803388e9",
      "cidr": "172.31.0.0/16",
      "region": "us_east_2",
      "id": "vpc-cca949a7",
      "accountNumber": "960952821882",
      "vpnGateways": [],
      "dhcpOptionsId": "dopt-1fc43e74",
      "instanceTenancy": "default",
      "isDefault": "true",
      "state": "available",
      "tags": [],
      "name": "",
      "vpcPeeringConnections": "null",
      "source": "Db"
    },
    "id": "sg-0e7363ccfa59809d5",
    "type": "SecurityGroup",
    "name": "split_test",
    "dome9Id": "1|33af7241-b8bb-453d-a3da-19c2803388e9|rg|16|sg|sg-0e7363ccfa59809d5-87862",
    "accountNumber": "960952821882",
    "region": "us_east_2",
    "source": "db",
    "tags": [],
    "externalFindings": "null"
  },
  "remediationActions": []
}

    output_message['ReportTime'] = source_message.get('reportTime', 'N.A')

    if (source_message.get('account')):
        output_message['Account id'] = source_message['account'].get('id', 'N.A')

    output_message['findingKey'] = source_message.get('findingKey', 'N.A')
    try:
        post_to_sns = handle_event(source_message, output_message)
    except Exception as e:
        post_to_sns = True
        output_message['Handle event failed'] = str(e)

    print(f'{__file__} - output message - {output_message}')

    # After the bot is called, post it to SNS for output logging
    if SNS_TOPIC_ARN != '' and post_to_sns:
        sendEvent(output_message, SNS_TOPIC_ARN)

    if not SNS_TOPIC_ARN:
        print(f'{__file__} - SNS topic out was not defined!')

    send_logs_to_dome9 = os.getenv('SEND_LOGS_TO_DOME9', '')
    print(f'{__file__} - send_logs_to_dome9 {send_logs_to_dome9}')
    if(send_logs_to_dome9 != 'false' and send_logs_to_dome9 != 'False'):
        send_logs(output_message, start_time, source_message.get('account').get('vendor'))
    return

if __name__ == '__main__':
    lambda_handler(1,2)