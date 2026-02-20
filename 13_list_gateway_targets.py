#!/usr/bin/env python3
"""
Script to list AgentCore Gateway targets.

Prerequisites:
- gateway_config.json (from gateway creation)
"""

import json
import boto3
import sys

print("=" * 80)
print("LIST GATEWAY TARGETS")
print("=" * 80)
print()

# ============================================================================
# STEP 1: Load Configuration
# ============================================================================
print("Step 1: Loading gateway configuration...")

try:
    with open('gateway_config.json') as f:
        gateway_config = json.load(f)
    print(f"✓ Loaded gateway_config.json")
    print(f"  Gateway ID: {gateway_config['gateway_id']}")
    print(f"  Gateway URL: {gateway_config['gateway_url']}")
except FileNotFoundError:
    print("❌ Error: gateway_config.json not found")
    print("   Run 11_create_gateway.py first")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error loading gateway_config.json: {e}")
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
# STEP 3: List Gateway Targets
# ============================================================================
print()
print("Step 3: Listing gateway targets...")
print(f"  Gateway: {gateway_config['gateway_id']}")

try:
    response = gateway_client.list_gateway_targets(
        gatewayIdentifier=gateway_config["gateway_id"]
    )
    
    targets = response.get("items", [])
    
    print(f"✓ Found {len(targets)} target(s)")
    
except Exception as e:
    print(f"❌ Error listing targets: {e}")
    sys.exit(1)

# ============================================================================
# STEP 4: Display Target Details
# ============================================================================
print()
print("=" * 80)
print("GATEWAY TARGETS")
print("=" * 80)

if not targets:
    print()
    print("No targets found. Add targets using 12_add_lambda_to_gateway.py")
    print()
else:
    for i, target in enumerate(targets, 1):
        print()
        print(f"Target {i}: {target.get('name', 'N/A')}")
        print("-" * 80)
        print(f"  Target ID: {target.get('targetId', 'N/A')}")
        print(f"  Status: {target.get('status', 'unknown')}")
        print(f"  Description: {target.get('description', 'N/A')}")
        
        # Display additional details if available
        if 'createdAt' in target:
            print(f"  Created At: {target['createdAt']}")
        if 'updatedAt' in target:
            print(f"  Updated At: {target['updatedAt']}")
        
        # Display target configuration type
        if 'targetConfiguration' in target:
            config = target['targetConfiguration']
            if 'mcp' in config:
                print(f"  Type: MCP")
                if 'lambda' in config['mcp']:
                    lambda_info = config['mcp']['lambda']
                    if 'lambdaArn' in lambda_info:
                        print(f"  Lambda ARN: {lambda_info['lambdaArn']}")
                    if 'toolSchema' in lambda_info:
                        tool_schema = lambda_info['toolSchema']
                        if 'inlinePayload' in tool_schema:
                            tools = tool_schema['inlinePayload']
                            print(f"  Tools: {len(tools)}")
                            for tool in tools:
                                print(f"    • {tool.get('name', 'N/A')}: {tool.get('description', 'N/A')}")

# ============================================================================
# SUMMARY
# ============================================================================
print()
print("=" * 80)
print("SUMMARY")
print("=" * 80)
print()
print(f"Gateway ID: {gateway_config['gateway_id']}")
print(f"Gateway URL: {gateway_config['gateway_url']}")
print(f"Total Targets: {len(targets)}")
print()

if targets:
    print("Status Overview:")
    status_counts = {}
    for target in targets:
        status = target.get('status', 'unknown')
        status_counts[status] = status_counts.get(status, 0) + 1
    
    for status, count in status_counts.items():
        print(f"  • {status}: {count}")
    print()
    print("All targets are ready to be used by agents via MCP!")
else:
    print("No targets registered yet.")
    print("Add targets using: python3 12_add_lambda_to_gateway.py")

print("=" * 80)
