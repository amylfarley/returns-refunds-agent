#!/usr/bin/env python3
"""
Script to create AgentCore Gateway.

Prerequisites:
- cognito_config.json (from Cognito setup)
- gateway_role_config.json (from IAM role setup)
"""

import json
import boto3
import sys

print("=" * 80)
print("AGENTCORE GATEWAY CREATION")
print("=" * 80)
print()

# ============================================================================
# STEP 1: Load Configuration Files
# ============================================================================
print("Step 1: Loading configuration files...")

try:
    with open('cognito_config.json') as f:
        cognito_config = json.load(f)
    print(f"✓ Loaded cognito_config.json")
    print(f"  Client ID: {cognito_config['client_id']}")
    print(f"  Discovery URL: {cognito_config['discovery_url']}")
except FileNotFoundError:
    print("❌ Error: cognito_config.json not found")
    print("   Run 08_create_cognito.py first")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error loading cognito_config.json: {e}")
    sys.exit(1)

try:
    with open('gateway_role_config.json') as f:
        role_config = json.load(f)
    print(f"✓ Loaded gateway_role_config.json")
    print(f"  Role ARN: {role_config['role_arn']}")
except FileNotFoundError:
    print("❌ Error: gateway_role_config.json not found")
    print("   Run 09_create_gateway_role.py first")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error loading gateway_role_config.json: {e}")
    sys.exit(1)

# ============================================================================
# STEP 2: Initialize AgentCore Client
# ============================================================================
print()
print("Step 2: Initializing AgentCore control plane client...")

try:
    gateway_client = boto3.client("bedrock-agentcore-control", region_name='us-west-2')
    print("✓ Client initialized")
except Exception as e:
    print(f"❌ Error initializing client: {e}")
    sys.exit(1)

# ============================================================================
# STEP 3: Build Authorization Configuration
# ============================================================================
print()
print("Step 3: Building authorization configuration...")

# Build auth configuration for Cognito JWT
auth_config = {
    "customJWTAuthorizer": {
        "allowedClients": [cognito_config["client_id"]],
        "discoveryUrl": cognito_config["discovery_url"]
    }
}

print("✓ Authorization configuration created")
print(f"  Authorizer Type: CUSTOM_JWT")
print(f"  Allowed Clients: {cognito_config['client_id']}")

# ============================================================================
# STEP 4: Create Gateway
# ============================================================================
print()
print("Step 4: Creating AgentCore Gateway...")
print(f"  Name: ReturnsRefundsGateway")
print(f"  Protocol: MCP")
print(f"  Region: us-west-2")

try:
    create_response = gateway_client.create_gateway(
        name="ReturnsRefundsGateway",
        roleArn=role_config["role_arn"],
        protocolType="MCP",
        authorizerType="CUSTOM_JWT",
        authorizerConfiguration=auth_config,
        description="Gateway for returns and refunds agent tools"
    )
    
    # Extract gateway details
    gateway_id = create_response["gatewayId"]
    gateway_url = create_response["gatewayUrl"]
    gateway_arn = create_response["gatewayArn"]
    
    print(f"✓ Gateway created successfully!")
    print(f"  Gateway ID: {gateway_id}")
    print(f"  Gateway URL: {gateway_url}")
    print(f"  Gateway ARN: {gateway_arn}")
    
except Exception as e:
    print(f"❌ Error creating gateway: {e}")
    sys.exit(1)

# ============================================================================
# STEP 5: Save Configuration
# ============================================================================
print()
print("Step 5: Saving configuration to gateway_config.json...")

# Save gateway config (using 'id' to match reference code pattern)
config = {
    "id": gateway_id,
    "gateway_id": gateway_id,  # Keep for backward compatibility
    "gateway_url": gateway_url,
    "gateway_arn": gateway_arn,
    "name": "ReturnsRefundsGateway",
    "region": "us-west-2"
}

try:
    with open('gateway_config.json', 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"✓ Configuration saved to gateway_config.json")
    
except Exception as e:
    print(f"❌ Error saving configuration: {e}")
    sys.exit(1)

# ============================================================================
# SUMMARY
# ============================================================================
print()
print("=" * 80)
print("GATEWAY CREATION COMPLETE")
print("=" * 80)
print()
print(f"Gateway ID: {gateway_id}")
print(f"Gateway URL: {gateway_url}")
print(f"Gateway ARN: {gateway_arn}")
print()
print("Authentication:")
print(f"  ✓ Cognito JWT authorization configured")
print(f"  ✓ Client ID: {cognito_config['client_id']}")
print()
print("Configuration saved to: gateway_config.json")
print()
print("Next steps:")
print("  1. Add Lambda targets to the gateway")
print("  2. Connect your agent to the gateway")
print("=" * 80)
