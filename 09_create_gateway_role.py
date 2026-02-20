#!/usr/bin/env python3
"""
Script to create IAM role for AgentCore Gateway.

This script creates:
- IAM role that the gateway can assume
- Trust policy allowing AgentCore Gateway service to assume the role
- Permissions policy to invoke Lambda functions
"""

import boto3
import json
import time
import uuid

# Configuration
REGION = 'us-west-2'
ROLE_NAME = f'AgentCoreGatewayRole-{uuid.uuid4().hex[:8]}'
POLICY_NAME = f'AgentCoreGatewayPolicy-{uuid.uuid4().hex[:8]}'

print("=" * 80)
print("IAM ROLE SETUP FOR AGENTCORE GATEWAY")
print("=" * 80)
print()

# Create IAM client
iam_client = boto3.client('iam')
sts_client = boto3.client('sts', region_name=REGION)

# Get AWS account ID
try:
    account_id = sts_client.get_caller_identity()['Account']
    print(f"AWS Account ID: {account_id}")
    print()
except Exception as e:
    print(f"❌ Error getting account ID: {e}")
    exit(1)

# ============================================================================
# STEP 1: Create Trust Policy (who can assume this role)
# ============================================================================
print("Step 1: Creating trust policy for AgentCore Gateway...")

# Trust policy allows AgentCore Gateway service to assume this role
trust_policy = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {
                "Service": "bedrock-agentcore.amazonaws.com"
            },
            "Action": "sts:AssumeRole",
            "Condition": {
                "StringEquals": {
                    "aws:SourceAccount": account_id
                }
            }
        }
    ]
}

print("✓ Trust policy created")
print(f"  Allows: bedrock-agentcore.amazonaws.com to assume role")

# ============================================================================
# STEP 2: Create IAM Role
# ============================================================================
print()
print("Step 2: Creating IAM role...")
print(f"  Role Name: {ROLE_NAME}")

try:
    role_response = iam_client.create_role(
        RoleName=ROLE_NAME,
        AssumeRolePolicyDocument=json.dumps(trust_policy),
        Description='IAM role for AgentCore Gateway to invoke Lambda functions',
        MaxSessionDuration=3600
    )
    
    role_arn = role_response['Role']['Arn']
    print(f"✓ Role created: {role_arn}")
    
except Exception as e:
    print(f"❌ Error creating role: {e}")
    exit(1)

# ============================================================================
# STEP 3: Create Permissions Policy (what the role can do)
# ============================================================================
print()
print("Step 3: Creating permissions policy...")

# Permissions policy allows invoking Lambda functions
permissions_policy = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "lambda:InvokeFunction"
            ],
            "Resource": f"arn:aws:lambda:{REGION}:{account_id}:function:*"
        }
    ]
}

try:
    policy_response = iam_client.create_policy(
        PolicyName=POLICY_NAME,
        PolicyDocument=json.dumps(permissions_policy),
        Description='Allows AgentCore Gateway to invoke Lambda functions'
    )
    
    policy_arn = policy_response['Policy']['Arn']
    print(f"✓ Policy created: {policy_arn}")
    print(f"  Grants: lambda:InvokeFunction on all Lambda functions")
    
except Exception as e:
    print(f"❌ Error creating policy: {e}")
    # Cleanup role
    iam_client.delete_role(RoleName=ROLE_NAME)
    exit(1)

# ============================================================================
# STEP 4: Attach Policy to Role
# ============================================================================
print()
print("Step 4: Attaching policy to role...")

try:
    iam_client.attach_role_policy(
        RoleName=ROLE_NAME,
        PolicyArn=policy_arn
    )
    
    print(f"✓ Policy attached to role")
    
except Exception as e:
    print(f"❌ Error attaching policy: {e}")
    # Cleanup
    iam_client.delete_policy(PolicyArn=policy_arn)
    iam_client.delete_role(RoleName=ROLE_NAME)
    exit(1)

# ============================================================================
# STEP 5: Wait for IAM propagation
# ============================================================================
print()
print("Step 5: Waiting for IAM propagation...")
print("  (IAM changes can take a few seconds to propagate)")

time.sleep(10)
print("✓ IAM propagation complete")

# ============================================================================
# STEP 6: Save Configuration
# ============================================================================
print()
print("Step 6: Saving configuration to gateway_role_config.json...")

config = {
    "role_arn": role_arn,
    "role_name": ROLE_NAME,
    "policy_arn": policy_arn,
    "policy_name": POLICY_NAME,
    "region": REGION,
    "account_id": account_id
}

try:
    with open('gateway_role_config.json', 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"✓ Configuration saved to gateway_role_config.json")
    
except Exception as e:
    print(f"❌ Error saving configuration: {e}")
    exit(1)

# ============================================================================
# SUMMARY
# ============================================================================
print()
print("=" * 80)
print("IAM ROLE SETUP COMPLETE")
print("=" * 80)
print()
print(f"Role ARN: {role_arn}")
print(f"Role Name: {ROLE_NAME}")
print(f"Policy ARN: {policy_arn}")
print()
print("Permissions granted:")
print("  ✓ Invoke Lambda functions in this account")
print()
print("Configuration saved to: gateway_role_config.json")
print()
print("This role allows the gateway to:")
print("  ✓ Call Lambda functions as tools")
print("  ✓ Execute on behalf of the agent")
print("=" * 80)
