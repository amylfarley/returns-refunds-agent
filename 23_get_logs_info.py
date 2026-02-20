#!/usr/bin/env python3
"""
Script to get CloudWatch log group information for AgentCore Runtime agent.

Provides:
- Log group name
- AWS CLI commands for viewing logs
- CloudWatch console URLs
- Log stream information
"""

import json
import os
from datetime import datetime

print("=" * 80)
print("CLOUDWATCH LOGS INFORMATION")
print("=" * 80)

# Load runtime configuration
if not os.path.exists('runtime_config.json'):
    print("\n❌ Error: Agent not deployed yet")
    print("Please run 19_deploy_agent.py first")
    exit(1)

with open('runtime_config.json') as f:
    runtime_config = json.load(f)

agent_arn = runtime_config["agent_arn"]
agent_name = runtime_config["agent_name"]
region = runtime_config.get("region", "us-west-2")

# Extract agent ID from ARN
agent_id = agent_arn.split('/')[-1]

# Build log group name
log_group = f"/aws/bedrock-agentcore/runtimes/{agent_id}-DEFAULT"

# Get current date for log stream prefix
current_date = datetime.now().strftime("%Y/%m/%d")

print(f"\nAgent Information:")
print(f"  Agent Name: {agent_name}")
print(f"  Agent ARN: {agent_arn}")
print(f"  Agent ID: {agent_id}")
print(f"  Region: {region}")

print(f"\nLog Group Information:")
print(f"  Log Group: {log_group}")
print(f"  Log Stream Prefix: {current_date}/[runtime-logs]")

# CloudWatch Console URL
import urllib.parse
encoded_log_group = urllib.parse.quote(log_group)
console_url = (
    f"https://console.aws.amazon.com/cloudwatch/home?"
    f"region={region}#logsV2:log-groups/log-group/{encoded_log_group}"
)

print("\n" + "=" * 80)
print("CLOUDWATCH CONSOLE")
print("=" * 80)
print(f"\nOpen in browser:")
print(console_url)

print("\n" + "=" * 80)
print("AWS CLI COMMANDS")
print("=" * 80)

print("\n1. Tail Logs in Real-Time (Follow Mode)")
print("-" * 80)
tail_command = f'aws logs tail {log_group} --follow --region {region}'
print(tail_command)

print("\n2. View Recent Logs (Last Hour)")
print("-" * 80)
recent_command = f'aws logs tail {log_group} --since 1h --region {region}'
print(recent_command)

print("\n3. View Logs from Last 10 Minutes")
print("-" * 80)
recent_10m_command = f'aws logs tail {log_group} --since 10m --region {region}'
print(recent_10m_command)

print("\n4. View Logs from Last 24 Hours")
print("-" * 80)
recent_24h_command = f'aws logs tail {log_group} --since 24h --region {region}'
print(recent_24h_command)

print("\n5. Filter Logs for Errors")
print("-" * 80)
error_command = f'''aws logs filter-log-events \\
  --log-group-name {log_group} \\
  --filter-pattern "ERROR" \\
  --region {region}'''
print(error_command)

print("\n6. Filter Logs for Tool Invocations")
print("-" * 80)
tool_command = f'''aws logs filter-log-events \\
  --log-group-name {log_group} \\
  --filter-pattern "lookup_order" \\
  --region {region}'''
print(tool_command)

print("\n7. Get Log Streams")
print("-" * 80)
streams_command = f'''aws logs describe-log-streams \\
  --log-group-name {log_group} \\
  --order-by LastEventTime \\
  --descending \\
  --max-items 10 \\
  --region {region}'''
print(streams_command)

print("\n8. CloudWatch Insights Query")
print("-" * 80)
insights_command = f'''aws logs start-query \\
  --log-group-name {log_group} \\
  --start-time $(date -d '1 hour ago' +%s) \\
  --end-time $(date +%s) \\
  --query-string 'fields @timestamp, @message | sort @timestamp desc | limit 20' \\
  --region {region}'''
print(insights_command)

print("\n" + "=" * 80)
print("QUICK REFERENCE")
print("=" * 80)

print(f"""
Log Group Name:
  {log_group}

Region:
  {region}

Agent ARN:
  {agent_arn}

Most Common Commands:
  # View recent logs
  aws logs tail {log_group} --since 1h --region {region}

  # Follow logs in real-time
  aws logs tail {log_group} --follow --region {region}

  # Find errors
  aws logs filter-log-events --log-group-name {log_group} --filter-pattern "ERROR" --region {region}
""")

print("=" * 80)
print("ADDITIONAL RESOURCES")
print("=" * 80)

print(f"""
GenAI Observability Dashboard:
  https://console.aws.amazon.com/cloudwatch/home?region={region}#gen-ai-observability/agent-core

X-Ray Service Map:
  https://console.aws.amazon.com/xray/home?region={region}#/service-map

For more monitoring options:
  python3 22_monitor_agent.py

For complete monitoring guide:
  See MONITORING_GUIDE.md
""")

print("=" * 80)
