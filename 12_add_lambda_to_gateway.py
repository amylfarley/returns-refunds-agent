#!/usr/bin/env python3
"""
Script to add Lambda target to AgentCore Gateway.

Prerequisites:
- gateway_config.json (from gateway creation)
- lambda_config.json (from Lambda creation)
"""

import json
import boto3
import sys

print("=" * 80)
print("ADD LAMBDA TARGET TO GATEWAY")
print("=" * 80)
print()

# ============================================================================
# STEP 1: Load Configuration Files
# ============================================================================
print("Step 1: Loading configuration files...")

try:
    with open('gateway_config.json') as f:
        gateway_config = json.load(f)
    print(f"✓ Loaded gateway_config.json")
    print(f"  Gateway ID: {gateway_config['gateway_id']}")
except FileNotFoundError:
    print("❌ Error: gateway_config.json not found")
    print("   Run 11_create_gateway.py first")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error loading gateway_config.json: {e}")
    sys.exit(1)

try:
    with open('lambda_config.json') as f:
        lambda_config = json.load(f)
    print(f"✓ Loaded lambda_config.json")
    print(f"  Lambda ARN: {lambda_config['function_arn']}")
    print(f"  Tool Name: {lambda_config['tool_name']}")
except FileNotFoundError:
    print("❌ Error: lambda_config.json not found")
    print("   Run 10_create_lambda.py first")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error loading lambda_config.json: {e}")
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
# STEP 3: Prepare Lambda Target Configuration
# ============================================================================
print()
print("Step 3: Preparing Lambda target configuration...")

# Extract Lambda ARN and tool schema from config
lambda_arn = lambda_config['function_arn']
tool_schema = lambda_config['tool_schema']['inlinePayload']

print(f"✓ Lambda ARN: {lambda_arn}")
print(f"✓ Tool Schema loaded:")
for tool in tool_schema:
    print(f"    - {tool['name']}: {tool['description']}")

# Build Lambda target configuration with MCP protocol
lambda_target_config = {
    "mcp": {
        "lambda": {
            "lambdaArn": lambda_arn,
            "toolSchema": {
                "inlinePayload": tool_schema
            }
        }
    }
}

# Use gateway's IAM role for Lambda invocation
credential_config = [{"credentialProviderType": "GATEWAY_IAM_ROLE"}]

print("✓ Target configuration prepared")
print(f"  Protocol: MCP")
print(f"  Credential Provider: GATEWAY_IAM_ROLE")

# ============================================================================
# STEP 4: Add Lambda Target to Gateway
# ============================================================================
print()
print("Step 4: Adding Lambda target to gateway...")
print(f"  Gateway ID: {gateway_config['gateway_id']}")
print(f"  Target Name: OrderLookup")

try:
    create_response = gateway_client.create_gateway_target(
        gatewayIdentifier=gateway_config["gateway_id"],
        name="OrderLookup",
        description="Lambda function to look up order details by order ID",
        targetConfiguration=lambda_target_config,
        credentialProviderConfigurations=credential_config
    )
    
    target_id = create_response["targetId"]
    
    print(f"✓ Lambda target added successfully!")
    print(f"  Target ID: {target_id}")
    
except Exception as e:
    print(f"❌ Error adding Lambda target: {e}")
    sys.exit(1)

# ============================================================================
# STEP 5: Update Gateway Configuration
# ============================================================================
print()
print("Step 5: Updating gateway configuration...")

# Add target info to gateway config
gateway_config['targets'] = gateway_config.get('targets', [])
gateway_config['targets'].append({
    "target_id": target_id,
    "target_name": "OrderLookup",
    "lambda_arn": lambda_arn,
    "tool_name": lambda_config['tool_name']
})

try:
    with open('gateway_config.json', 'w') as f:
        json.dump(gateway_config, f, indent=2)
    
    print(f"✓ Gateway configuration updated")
    
except Exception as e:
    print(f"❌ Error updating configuration: {e}")
    sys.exit(1)

# ============================================================================
# SUMMARY
# ============================================================================
print()
print("=" * 80)
print("LAMBDA TARGET ADDED TO GATEWAY")
print("=" * 80)
print()
print(f"Gateway ID: {gateway_config['gateway_id']}")
print(f"Gateway URL: {gateway_config['gateway_url']}")
print()
print(f"Target ID: {target_id}")
print(f"Target Name: OrderLookup")
print(f"Lambda ARN: {lambda_arn}")
print()
print("Available Tools:")
for tool in tool_schema:
    print(f"  • {tool['name']}")
    print(f"    Description: {tool['description']}")
    print(f"    Input: {', '.join(tool['inputSchema']['required'])}")
print()
print("The gateway now exposes the Lambda function as an MCP tool!")
print("Your agent can discover and use this tool automatically.")
print("=" * 80)
