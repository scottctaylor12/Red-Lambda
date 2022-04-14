# Red-Lambda

Red Lambda is an AWS CloudFormation template that automatically deploys red team infrastructure in the cloud.
My blog post covers more details about the background of this project.

## Overview

A basic red team infrastructure is deployed using the `lamda.yml` AWS cloudformation template.
Infrastructure includes:
* VPC and Subnet
* EC2 with SSM Enabled for C2
* Lambda Function to act as redirector
* Lambda Function URL to expose redirector to internet

The lambda function python code is embedded in the cloudformation template.
However, I've copied it in the `lambda.py` file to review. 

## Prerequisites

1. AWS CLI \
   https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-configure.html
2. AWS CLI Session Manager Plugin \
   https://docs.aws.amazon.com/systems-manager/latest/userguide/session-manager-working-with-install-plugin.html

## Deploying/Deleting Infrastructure

From the command line, run the following command to start the creating infrastructure:
```
aws cloudformation deploy --stack-name Red --template-file red.yml --capabilities CAPABILITY_NAMED_IAM
```

From the command line, run the following command to *destroy* the infrastructure:
```
aws cloudformation delete-stack --stack-name Red
```

## Retrieving Resource Information

After deploying the infrastructure, use the following aws-cli commands to find necessary information.

List EC2 instances:
```
aws ec2 describe-instances --query 'Reservations[*].Instances[0].{Name:Tags[?Key==`Name`].Value|[0],Instance:InstanceId,IP:PublicIpAddress, State:State.Name}' --output table
```

## Accessing Infrastructure

**No need for internet facing SSH systems or jump boxes!** \
Simply use AWS Systems Manager (SSM) from the AWS CLI to interact with your infrastructure.

Access any of the EC2 instances by using the AWS CLI through the `aws ssm` command:
```
aws ssm start-session --target <instance id>
```

Use SSM to port forward to your local machine:
```
aws ssm start-session --target <instance id> --document-name AWS-StartPortForwardingSession --parameters "portNumber"=["80"],"localPortNumber"=["1234"]
```
*Note: This is helpful if your C2 has a web management interface that you need to access locally.*

## Final Topology
![AWS Topology](/red-lambda-aws-topo.png)