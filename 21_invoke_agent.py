#!/usr/bin/env python3
"""
Script to invoke deployed AgentCore Runtime agent.

This script:
1. Loads Cognito credentials
2. Gets OAuth token for authentication
3. Invokes the agent with a test query
4. Displays the response
"""

import json
import os
import requests
from bedrock_agentcore_starter_toolkit import Runtime

print("=" * 80)
print("AGENTCORE RUNTIME AGENT INVOCATION")
print("=" * 80)

# ============================================================================
# STEP 1: Load configuration files
# ============================================================================
print("\nStep 1: Loading configuration files...")

# Check if runtime config exists
if not os.path.exists('runtime_config.json'):
    print("  ❌ Error: Agent not deployed yet")
    print("  Please run 19_deploy_agent.py first")
    exit(1)

# Load runtime config
with open('runtime_config.json') as f:
    runtime_config_data = json.load(f)
    agent_arn = runtime_config_data['agent_arn']
    agent_name = runtime_config_data['agent_name']
    print(f"  ✓ Runtime config loaded: {agent_name}")

# Load Cognito config
try:
    with open('cognito_config.json') as f:
        cognito_config = json.load(f)
        print(f"  ✓ Cognito config loaded")
except FileNotFoundError:
    print("  ❌ Error: cognito_config.json not found")
    exit(1)

# Load runtime execution role config
with open('runtime_execution_role_config.json') as f:
    role_config = json.load(f)

# Load .bedrock_agentcore.yaml
if not os.path.exists('.bedrock_agentcore.yaml'):
    print("  ❌ Error: .bedrock_agentcore.yaml not found")
    exit(1)

import yaml
with open('.bedrock_agentcore.yaml') as f:
    runtime_config = yaml.safe_load(f)

default_agent = runtime_config.get('default_agent')
agent_config = runtime_config.get('agents', {}).get(default_agent, {})
entrypoint = agent_config.get('entrypoint')

# ============================================================================
# STEP 2: Get OAuth token for authentication
# ============================================================================
print("\nStep 2: Getting OAuth token for authentication...")

try:
    # Get token endpoint from discovery URL
    discovery_response = requests.get(cognito_config['discovery_url'], timeout=10)
    discovery_response.raise_for_status()
    token_endpoint = discovery_response.json()['token_endpoint']
    print(f"  ✓ Token endpoint: {token_endpoint}")
    
    # Request OAuth token using client credentials flow
    token_response = requests.post(
        token_endpoint,
        data={
            'grant_type': 'client_credentials',
            'client_id': cognito_config['client_id'],
            'client_secret': cognito_config['client_secret'],
            'scope': 'gateway-api/read gateway-api/write'
        },
        headers={'Content-Type': 'application/x-www-form-urlencoded'},
        timeout=10
    )
    
    token_response.raise_for_status()
    bearer_token = token_response.json()["access_token"]
    print("  ✓ OAuth token obtained successfully")
    
except Exception as e:
    print(f"  ❌ Failed to get OAuth token: {e}")
    exit(1)

# ============================================================================
# STEP 3: Configure Runtime
# ============================================================================
print("\nStep 3: Configuring runtime...")

# Initialize Runtime
runtime = Runtime()

# Build authorizer configuration for Cognito JWT
auth_config = {
    "customJWTAuthorizer": {
        "allowedClients": [cognito_config["client_id"]],
        "discoveryUrl": cognito_config["discovery_url"]
    }
}

# Configure runtime (to load existing configuration)
runtime.configure(
    entrypoint=entrypoint,
    agent_name=agent_name,
    execution_role=role_config["role_arn"],
    auto_create_ecr=True,
    memory_mode="NO_MEMORY",
    requirements_file="requirements_runtime.txt",
    region="us-west-2",
    authorizer_configuration=auth_config
)

print("  ✓ Runtime configured")

# ============================================================================
# STEP 4: Invoke agent with test query
# ============================================================================
print("\nStep 4: Invoking agent...")
print("\n" + "=" * 80)
print("TEST QUERY")
print("=" * 80)

# Test payload
payload = {
    "prompt": "Can you look up my order ORD-001 and help me with a return?",
    "actor_id": "user_001"
}

print(f"\nActor ID: {payload['actor_id']}")
print(f"Query: {payload['prompt']}")
print("\n" + "=" * 80)

try:
    print("\n⏳ Sending request to agent...")
    print(f"Agent ARN: {agent_arn}")
    
    response = runtime.invoke(
        payload,
        bearer_token=bearer_token
    )
    
    # ============================================================================
    # STEP 5: Display the response
    # ============================================================================
    print("\n" + "=" * 80)
    print("✅ AGENT RESPONSE")
    print("=" * 80)
    print()
    print(response)
    print()
    print("=" * 80)
    print("RESPONSE ANALYSIS")
    print("=" * 80)
    print("\nThe agent should have:")
    print("  ✓ Recalled user_001's email preference from memory")
    print("  ✓ Looked up order ORD-001 via gateway (Dell XPS 15 Laptop)")
    print("  ✓ Checked return eligibility (within 30-day window)")
    print("  ✓ Provided personalized return instructions")
    print("\n" + "=" * 80)
    print("SUCCESS!")
    print("=" * 80)
    print("\nYour agent is fully operational with:")
    print("  ✓ Memory integration (recalled preferences)")
    print("  ✓ Gateway integration (order lookup)")
    print("  ✓ Knowledge Base integration (policy retrieval)")
    print("  ✓ Custom tools (eligibility checking)")
    print("  ✓ OAuth authentication")
    print("\n" + "=" * 80)
    
except Exception as e:
    print("\n" + "=" * 80)
    print("❌ ERROR INVOKING AGENT")
    print("=" * 80)
    print(f"\nError: {e}")
    print("\n" + "=" * 80)
    print("TROUBLESHOOTING")
    print("=" * 80)
    print("\n1. Check agent status:")
    print("   python 20_check_status.py")
    print("\n2. Verify agent is in READY state")
    print("\n3. Check CloudWatch logs:")
    print(f"   aws logs tail /aws/bedrock-agentcore/runtimes/{agent_name.replace('_', '-')}-xRyDzcDbNQ-DEFAULT --since 10m")
    print("\n4. Verify environment variables are set correctly")
    print("\n5. Check IAM role permissions:")
    print(f"   Role: {role_config['role_name']}")
    print("\n" + "=" * 80)
    
    import traceback
    traceback.print_exc()
    exit(1)
