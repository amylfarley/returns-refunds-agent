#!/usr/bin/env python3
"""
Script to deploy agent to AgentCore Runtime.

This script:
1. Loads all configuration files
2. Configures runtime deployment settings
3. Sets environment variables
4. Deploys to AgentCore Runtime
5. Saves agent ARN to runtime_config.json
"""

import json
import os
from bedrock_agentcore_starter_toolkit import Runtime

print("=" * 80)
print("AGENTCORE RUNTIME DEPLOYMENT")
print("=" * 80)

# ============================================================================
# STEP 1: Load all configuration files
# ============================================================================
print("\nStep 1: Loading configuration files...")

config_files = {}

# Load memory config
try:
    with open('memory_config.json') as f:
        config_files['memory'] = json.load(f)
        print(f"  ✓ Memory config loaded: {config_files['memory']['memory_id']}")
except FileNotFoundError:
    print("  ✗ memory_config.json not found")
    exit(1)

# Load gateway config
try:
    with open('gateway_config.json') as f:
        config_files['gateway'] = json.load(f)
        print(f"  ✓ Gateway config loaded: {config_files['gateway']['gateway_url']}")
except FileNotFoundError:
    print("  ✗ gateway_config.json not found")
    exit(1)

# Load Cognito config
try:
    with open('cognito_config.json') as f:
        config_files['cognito'] = json.load(f)
        print(f"  ✓ Cognito config loaded: {config_files['cognito']['client_id']}")
except FileNotFoundError:
    print("  ✗ cognito_config.json not found")
    exit(1)

# Load runtime execution role config
try:
    with open('runtime_execution_role_config.json') as f:
        config_files['role'] = json.load(f)
        print(f"  ✓ Runtime role config loaded: {config_files['role']['role_name']}")
except FileNotFoundError:
    print("  ✗ runtime_execution_role_config.json not found")
    exit(1)

# Load knowledge base config
try:
    with open('kb_config.json') as f:
        config_files['kb'] = json.load(f)
        print(f"  ✓ Knowledge Base config loaded: {config_files['kb']['knowledge_base_id']}")
except FileNotFoundError:
    print("  ✗ kb_config.json not found")
    exit(1)

# ============================================================================
# STEP 2: Configure runtime deployment settings
# ============================================================================
print("\nStep 2: Configuring runtime deployment...")

# Initialize Runtime
runtime = Runtime()

# Build authorizer configuration for Cognito JWT
auth_config = {
    "customJWTAuthorizer": {
        "allowedClients": [config_files['cognito']["client_id"]],
        "discoveryUrl": config_files['cognito']["discovery_url"]
    }
}

# Configure runtime deployment
runtime.configure(
    entrypoint="17_runtime_agent.py",
    agent_name="returns_refunds_agent",
    execution_role=config_files['role']["role_arn"],
    auto_create_ecr=True,
    memory_mode="NO_MEMORY",  # Memory is handled via environment variables
    requirements_file="requirements_runtime.txt",
    region="us-west-2",
    authorizer_configuration=auth_config
)

print("  ✓ Runtime configured successfully")
print("  ✓ Configuration saved to .bedrock_agentcore.yaml")

# ============================================================================
# STEP 3: Build environment variables
# ============================================================================
print("\nStep 3: Setting environment variables...")

env_vars = {
    "MEMORY_ID": config_files['memory']["memory_id"],
    "KNOWLEDGE_BASE_ID": config_files['kb']["knowledge_base_id"],
    "GATEWAY_URL": config_files['gateway']["gateway_url"],
    "COGNITO_CLIENT_ID": config_files['cognito']["client_id"],
    "COGNITO_CLIENT_SECRET": config_files['cognito']["client_secret"],
    "COGNITO_DISCOVERY_URL": config_files['cognito']["discovery_url"],
    "OAUTH_SCOPES": "gateway-api/read gateway-api/write"
}

print("  Environment variables set:")
for key in env_vars:
    if "SECRET" in key:
        print(f"    {key}: ***")
    else:
        print(f"    {key}: {env_vars[key]}")

# ============================================================================
# STEP 4: Deploy to AgentCore Runtime
# ============================================================================
print("\n" + "=" * 80)
print("LAUNCHING AGENT TO AGENTCORE RUNTIME")
print("=" * 80)
print("\nThis process will:")
print("  1. Create CodeBuild project")
print("  2. Build Docker container from your agent code")
print("  3. Push container to Amazon ECR")
print("  4. Deploy to AgentCore Runtime")
print("\n⏱️  Expected time: 5-10 minutes")
print("\n☕ Grab a coffee while the deployment runs...")
print("=" * 80)

try:
    launch_result = runtime.launch(
        env_vars=env_vars,
        auto_update_on_conflict=True
    )
    
    agent_arn = launch_result.agent_arn
    
    print("\n✓ Agent deployment initiated!")
    print(f"  Agent ARN: {agent_arn}")
    
except Exception as e:
    print(f"\n✗ Deployment failed: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

# ============================================================================
# STEP 5: Save agent ARN to runtime_config.json
# ============================================================================
print("\nStep 5: Saving runtime configuration...")

runtime_output_config = {
    "agent_arn": agent_arn,
    "agent_name": "returns_refunds_agent",
    "region": "us-west-2",
    "memory_id": config_files['memory']["memory_id"],
    "gateway_url": config_files['gateway']["gateway_url"],
    "knowledge_base_id": config_files['kb']["knowledge_base_id"]
}

with open('runtime_config.json', 'w') as f:
    json.dump(runtime_output_config, f, indent=2)

print("  ✓ Configuration saved to runtime_config.json")

# ============================================================================
# SUMMARY
# ============================================================================
print("\n" + "=" * 80)
print("DEPLOYMENT SUMMARY")
print("=" * 80)
print(f"\nAgent ARN: {agent_arn}")
print(f"Agent Name: returns_refunds_agent")
print(f"Region: us-west-2")
print(f"Entrypoint: 17_runtime_agent.py")
print(f"Execution Role: {config_files['role']['role_name']}")
print("\nIntegrations:")
print(f"  ✓ Memory: {config_files['memory']['memory_id']}")
print(f"  ✓ Gateway: {config_files['gateway']['gateway_id']}")
print(f"  ✓ Knowledge Base: {config_files['kb']['knowledge_base_id']}")
print(f"  ✓ Authentication: Cognito JWT")

print("\n" + "=" * 80)
print("NEXT STEPS")
print("=" * 80)
print("\n1. Monitor deployment status:")
print("   The deployment is running in the background via CodeBuild")
print("   Check status with: python 20_check_runtime_status.py")
print("\n2. Wait for status to show 'READY' (may take 5-10 minutes)")
print("\n3. Once READY, test your agent:")
print("   Run: python 21_test_runtime_agent.py")
print("\n4. View logs and monitoring:")
print("   CloudWatch Logs: /aws/bedrock-agentcore/runtime/returns_refunds_agent")
print("   X-Ray Traces: Available in AWS Console")
print("\n" + "=" * 80)
