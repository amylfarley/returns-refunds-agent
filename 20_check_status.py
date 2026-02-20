#!/usr/bin/env python3
"""
Script to check AgentCore Runtime deployment status.

Monitors deployment until READY or FAILED state.
"""

import json
import os
import time
from bedrock_agentcore_starter_toolkit import Runtime

print("=" * 80)
print("AGENTCORE RUNTIME STATUS CHECK")
print("=" * 80)

# Check if runtime config exists
if not os.path.exists('runtime_config.json'):
    print("\n❌ Error: Agent not deployed yet")
    print("Please run 19_deploy_agent.py first")
    exit(1)

# Load runtime config
with open('runtime_config.json') as f:
    runtime_config_data = json.load(f)
    agent_arn = runtime_config_data['agent_arn']
    agent_name = runtime_config_data['agent_name']

print(f"\nAgent ARN: {agent_arn}")
print(f"Agent Name: {agent_name}")
print(f"Region: us-west-2")

# Load configuration files
with open('runtime_execution_role_config.json') as f:
    role_config = json.load(f)
with open('cognito_config.json') as f:
    cognito_config = json.load(f)

# Load .bedrock_agentcore.yaml to get agent configuration
if not os.path.exists('.bedrock_agentcore.yaml'):
    print("\n❌ Error: .bedrock_agentcore.yaml not found")
    print("Please run 19_deploy_agent.py first")
    exit(1)

import yaml
with open('.bedrock_agentcore.yaml') as f:
    runtime_config = yaml.safe_load(f)

default_agent = runtime_config.get('default_agent')
agent_config = runtime_config.get('agents', {}).get(default_agent, {})
entrypoint = agent_config.get('entrypoint')

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

# Monitor status until READY or FAILED
print("\n" + "=" * 80)
print("MONITORING DEPLOYMENT STATUS")
print("=" * 80)
print("\nChecking status every 10 seconds...")
print("Press Ctrl+C to stop monitoring\n")

check_count = 0
max_checks = 60  # Maximum 10 minutes (60 checks * 10 seconds)

try:
    while check_count < max_checks:
        check_count += 1
        
        try:
            # Check status
            status_response = runtime.status()
            status = status_response.endpoint.get("status", "UNKNOWN")
            
            timestamp = time.strftime("%H:%M:%S")
            print(f"[{timestamp}] Check #{check_count}: Status = {status}")
            
            # Check if we've reached a terminal state
            if status == "READY":
                print("\n" + "=" * 80)
                print("✅ AGENT IS READY!")
                print("=" * 80)
                print(f"\nAgent ARN: {agent_arn}")
                print(f"Status: {status}")
                print("\nEndpoint Details:")
                print(json.dumps(status_response.endpoint, indent=2, default=str))
                print("\n" + "=" * 80)
                print("NEXT STEPS")
                print("=" * 80)
                print("\n1. Test your agent:")
                print("   python 21_test_runtime_agent.py")
                print("\n2. View logs:")
                print(f"   aws logs tail /aws/bedrock-agentcore/runtimes/{agent_name.replace('_', '-')}-xRyDzcDbNQ-DEFAULT --follow")
                print("\n3. View observability dashboard:")
                print("   https://console.aws.amazon.com/cloudwatch/home?region=us-west-2#gen-ai-observability/agent-core")
                print("\n" + "=" * 80)
                break
            
            elif status in ["CREATE_FAILED", "UPDATE_FAILED", "FAILED"]:
                print("\n" + "=" * 80)
                print("❌ DEPLOYMENT FAILED!")
                print("=" * 80)
                print(f"\nAgent ARN: {agent_arn}")
                print(f"Status: {status}")
                print("\nEndpoint Details:")
                print(json.dumps(status_response.endpoint, indent=2, default=str))
                print("\n" + "=" * 80)
                print("TROUBLESHOOTING")
                print("=" * 80)
                print("\n1. Check CloudWatch logs for error details:")
                print(f"   aws logs tail /aws/bedrock-agentcore/runtimes/{agent_name.replace('_', '-')}-xRyDzcDbNQ-DEFAULT --since 1h")
                print("\n2. Check CodeBuild logs:")
                print("   aws codebuild list-builds-for-project --project-name bedrock-agentcore-returns_refunds_agent-builder")
                print("\n3. Verify IAM role permissions:")
                print(f"   Role: {role_config['role_name']}")
                print("\n4. Common issues:")
                print("   - Missing environment variables")
                print("   - IAM permission errors")
                print("   - Docker build failures")
                print("   - Invalid entrypoint file")
                print("\n" + "=" * 80)
                exit(1)
            
            elif status in ["CREATING", "UPDATING", "DELETING"]:
                # Still in progress
                if check_count % 6 == 0:  # Every minute
                    print(f"   ⏳ Still {status.lower()}... (elapsed: {check_count * 10}s)")
            
            else:
                print(f"   ⚠️  Unknown status: {status}")
            
            # Wait before next check (unless we're done)
            if status not in ["READY", "CREATE_FAILED", "UPDATE_FAILED", "FAILED"]:
                time.sleep(10)
            else:
                break
                
        except KeyboardInterrupt:
            print("\n\n⚠️  Monitoring stopped by user")
            print(f"Last known status: {status}")
            print("\nYou can resume monitoring by running this script again.")
            exit(0)
        except Exception as e:
            print(f"\n❌ Error checking status: {e}")
            import traceback
            traceback.print_exc()
            print("\nRetrying in 10 seconds...")
            time.sleep(10)
    
    # If we've exceeded max checks
    if check_count >= max_checks:
        print("\n" + "=" * 80)
        print("⏱️  TIMEOUT")
        print("=" * 80)
        print(f"\nDeployment is taking longer than expected ({max_checks * 10}s)")
        print(f"Last known status: {status}")
        print("\nThe deployment may still be in progress.")
        print("Check the AWS Console or run this script again later.")
        print("\n" + "=" * 80)

except Exception as e:
    print(f"\n❌ Fatal error: {e}")
    import traceback
    traceback.print_exc()
    exit(1)
