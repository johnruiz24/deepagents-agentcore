"""
IAM role creation utilities for AgentCore deployment.

Creates and manages the IAM role required for the Literacy Assessment Agent
with permissions for Bedrock, S3, Knowledge Bases, and CloudWatch.
"""

import os
import boto3
import json
import time
from boto3.session import Session

# AWS configuration
os.environ["AWS_PROFILE"] = "mll-dev"
os.environ["AWS_REGION"] = "eu-central-1"


def create_agentcore_role(agent_name):
    """
    Create or update IAM role for AgentCore with all necessary permissions.

    The role includes permissions for:
    - Bedrock model invocation (Claude Sonnet 4.5)
    - Bedrock Knowledge Base access (4 level-specific KBs)
    - S3 bucket access (reading KB files + writing assessments)
    - CloudWatch Logs (AgentCore automatic logging)
    - ECR (container image access)
    - X-Ray tracing
    - CloudWatch metrics
    - AgentCore workload identity

    Args:
        agent_name: Name of the agent (e.g., "literacy_assessment")

    Returns:
        dict: IAM role response from create_role API
    """
    boto_session = Session(
        profile_name=os.getenv("AWS_PROFILE"),
        region_name=os.getenv("AWS_REGION")
    )
    iam_client = boto_session.client('iam')
    agentcore_role_name = f'agentcore-{agent_name}-role-0511'
    region = boto_session.region_name
    account_id = boto_session.client("sts").get_caller_identity()["Account"]

    # S3 bucket for literacy framework
    s3_bucket_name = "literacy-framework-development-961105418118-eu-central-1"

    # Bedrock Knowledge Base IDs for all 4 levels
    kb_ids = {
        "level_1": "QADZTSAPWX",
        "level_2": "KGGD2PTQ2N",
        "level_3": "7MGFSODDVI",
        "level_4": "CHYWO1H6OM",
    }

    role_policy = {
        "Version": "2012-10-17",
        "Statement": [
            # Bedrock model invocation
            {
                "Sid": "BedrockModelPermissions",
                "Effect": "Allow",
                "Action": [
                    "bedrock:InvokeModel",
                    "bedrock:InvokeModelWithResponseStream"
                ],
                "Resource": "*"
            },
            # Bedrock Knowledge Base access
            {
                "Sid": "BedrockKnowledgeBasePermissions",
                "Effect": "Allow",
                "Action": [
                    "bedrock:Retrieve",
                    "bedrock:RetrieveAndGenerate"
                ],
                "Resource": [
                    f"arn:aws:bedrock:{region}:{account_id}:knowledge-base/{kb_ids['level_1']}",
                    f"arn:aws:bedrock:{region}:{account_id}:knowledge-base/{kb_ids['level_2']}",
                    f"arn:aws:bedrock:{region}:{account_id}:knowledge-base/{kb_ids['level_3']}",
                    f"arn:aws:bedrock:{region}:{account_id}:knowledge-base/{kb_ids['level_4']}"
                ]
            },
            # S3 permissions for reading KB files and writing assessments
            {
                "Sid": "S3ReadKnowledgeBasePermissions",
                "Effect": "Allow",
                "Action": [
                    "s3:GetObject",
                    "s3:ListBucket"
                ],
                "Resource": [
                    f"arn:aws:s3:::{s3_bucket_name}/learning_path/levels/*",
                    f"arn:aws:s3:::{s3_bucket_name}"
                ]
            },
            {
                "Sid": "S3WriteAssessmentPermissions",
                "Effect": "Allow",
                "Action": [
                    "s3:PutObject",
                    "s3:PutObjectAcl"
                ],
                "Resource": [
                    f"arn:aws:s3:::{s3_bucket_name}/learning_path/assessments/*"
                ]
            },
            # Marketplace permissions
            {
                "Sid": "MarketplacePermissions",
                "Effect": "Allow",
                "Action": [
                    "aws-marketplace:ViewSubscriptions"
                ],
                "Resource": "*"
            },
            # ECR image access
            {
                "Sid": "ECRImageAccess",
                "Effect": "Allow",
                "Action": [
                    "ecr:BatchGetImage",
                    "ecr:GetDownloadUrlForLayer"
                ],
                "Resource": [
                    f"arn:aws:ecr:{region}:{account_id}:repository/*"
                ]
            },
            {
                "Sid": "ECRTokenAccess",
                "Effect": "Allow",
                "Action": [
                    "ecr:GetAuthorizationToken"
                ],
                "Resource": "*"
            },
            # CloudWatch Logs permissions (AgentCore automatic logging)
            {
                "Effect": "Allow",
                "Action": [
                    "logs:DescribeLogStreams",
                    "logs:CreateLogGroup"
                ],
                "Resource": [
                    f"arn:aws:logs:{region}:{account_id}:log-group:/aws/bedrock-agentcore/runtimes/*"
                ]
            },
            {
                "Effect": "Allow",
                "Action": [
                    "logs:DescribeLogGroups"
                ],
                "Resource": [
                    f"arn:aws:logs:{region}:{account_id}:log-group:*"
                ]
            },
            {
                "Effect": "Allow",
                "Action": [
                    "logs:CreateLogStream",
                    "logs:PutLogEvents"
                ],
                "Resource": [
                    f"arn:aws:logs:{region}:{account_id}:log-group:/aws/bedrock-agentcore/runtimes/*:log-stream:*"
                ]
            },
            # X-Ray tracing
            {
                "Effect": "Allow",
                "Action": [
                    "xray:PutTraceSegments",
                    "xray:PutTelemetryRecords",
                    "xray:GetSamplingRules",
                    "xray:GetSamplingTargets"
                ],
                "Resource": ["*"]
            },
            # CloudWatch metrics
            {
                "Effect": "Allow",
                "Resource": "*",
                "Action": "cloudwatch:PutMetricData",
                "Condition": {
                    "StringEquals": {
                        "cloudwatch:namespace": "bedrock-agentcore"
                    }
                }
            },
            # AgentCore workload identity
            {
                "Sid": "GetAgentAccessToken",
                "Effect": "Allow",
                "Action": [
                    "bedrock-agentcore:GetWorkloadAccessToken",
                    "bedrock-agentcore:GetWorkloadAccessTokenForJWT",
                    "bedrock-agentcore:GetWorkloadAccessTokenForUserId"
                ],
                "Resource": [
                    f"arn:aws:bedrock-agentcore:{region}:{account_id}:workload-identity-directory/default",
                    f"arn:aws:bedrock-agentcore:{region}:{account_id}:workload-identity-directory/default/workload-identity/{agent_name}-*"
                ]
            }
        ]
    }

    assume_role_policy_document = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "AssumeRolePolicy",
                "Effect": "Allow",
                "Principal": {
                    "Service": "bedrock-agentcore.amazonaws.com"
                },
                "Action": "sts:AssumeRole",
                "Condition": {
                    "StringEquals": {
                        "aws:SourceAccount": f"{account_id}"
                    },
                    "ArnLike": {
                        "aws:SourceArn": f"arn:aws:bedrock-agentcore:{region}:{account_id}:*"
                    }
                }
            }
        ]
    }

    assume_role_policy_document_json = json.dumps(assume_role_policy_document)
    role_policy_document = json.dumps(role_policy)

    # Create or recreate IAM Role
    try:
        agentcore_iam_role = iam_client.create_role(
            RoleName=agentcore_role_name,
            AssumeRolePolicyDocument=assume_role_policy_document_json
        )
        print(f"✓ Created IAM role: {agentcore_role_name}")
        # Pause to ensure role is available
        time.sleep(10)
    except iam_client.exceptions.EntityAlreadyExistsException:
        print(f"Role {agentcore_role_name} already exists -- deleting and recreating...")

        # Delete existing policies
        policies = iam_client.list_role_policies(
            RoleName=agentcore_role_name,
            MaxItems=100
        )
        for policy_name in policies['PolicyNames']:
            iam_client.delete_role_policy(
                RoleName=agentcore_role_name,
                PolicyName=policy_name
            )

        # Delete role
        iam_client.delete_role(RoleName=agentcore_role_name)
        print(f"✓ Deleted old role: {agentcore_role_name}")

        # Recreate role
        agentcore_iam_role = iam_client.create_role(
            RoleName=agentcore_role_name,
            AssumeRolePolicyDocument=assume_role_policy_document_json
        )
        print(f"✓ Recreated IAM role: {agentcore_role_name}")
        time.sleep(10)

    # Attach inline policy
    try:
        iam_client.put_role_policy(
            PolicyDocument=role_policy_document,
            PolicyName="AgentCorePolicy",
            RoleName=agentcore_role_name
        )
        print(f"✓ Attached policy to role: {agentcore_role_name}")
    except Exception as e:
        print(f"✗ Error attaching policy: {e}")
        raise

    return agentcore_iam_role
