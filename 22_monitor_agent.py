#!/usr/bin/env python3
"""
Script to monitor deployed AgentCore Runtime agent.

Provides multiple monitoring options:
1. View recent logs
2. Tail logs in real-time
3. Get observability dashboard URL
4. Check agent metrics
"""

import json
import os
import subprocess
import sys

print("=" * 80)
print("AGENTCORE RUNTIME AGENT MONITORING")
print("=" * 80)

# Load runtime config
if not os.path.exists('runtime_config.json'):
    print("\n❌ Error: Agent not deployed yet")
    print("Please run 19_deploy_agent.py first")
    exit(1)

with open('runtime_config.json') as f:
    runtime_config = json.load(f)
    agent_arn = runtime_config['agent_arn']
    agent_name = runtime_config['agent_name']
    region = runtime_config['region']

print(f"\nAgent ARN: {agent_arn}")
print(f"Agent Name: {agent_name}")
print(f"Region: {region}")

# Extract agent ID from ARN
agent_id = agent_arn.split('/')[-1]
log_group = f"/aws/bedrock-agentcore/runtimes/{agent_id}-DEFAULT"

print("\n" + "=" * 80)
print("MONITORING OPTIONS")
print("=" * 80)

print("""
1. View Recent Logs (Last Hour)
2. Tail Logs in Real-Time (Follow Mode)
3. View Logs from Last 10 Minutes
4. View Logs from Last 24 Hours
5. Open CloudWatch Logs in Browser
6. View GenAI Observability Dashboard
7. Get X-Ray Trace Information
8. Exit

""")

choice = input("Select an option (1-8): ").strip()

if choice == "1":
    print("\n" + "=" * 80)
    print("RECENT LOGS (LAST HOUR)")
    print("=" * 80)
    print("\nFetching logs...\n")
    
    cmd = [
        "aws", "logs", "tail",
        log_group,
        "--since", "1h",
        "--region", region,
        "--format", "short"
    ]
    
    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("\n\nStopped by user")

elif choice == "2":
    print("\n" + "=" * 80)
    print("TAILING LOGS IN REAL-TIME")
    print("=" * 80)
    print("\nPress Ctrl+C to stop...\n")
    
    cmd = [
        "aws", "logs", "tail",
        log_group,
        "--follow",
        "--region", region,
        "--format", "short"
    ]
    
    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("\n\nStopped by user")

elif choice == "3":
    print("\n" + "=" * 80)
    print("RECENT LOGS (LAST 10 MINUTES)")
    print("=" * 80)
    print("\nFetching logs...\n")
    
    cmd = [
        "aws", "logs", "tail",
        log_group,
        "--since", "10m",
        "--region", region,
        "--format", "short"
    ]
    
    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("\n\nStopped by user")

elif choice == "4":
    print("\n" + "=" * 80)
    print("RECENT LOGS (LAST 24 HOURS)")
    print("=" * 80)
    print("\nFetching logs...\n")
    
    cmd = [
        "aws", "logs", "tail",
        log_group,
        "--since", "24h",
        "--region", region,
        "--format", "short"
    ]
    
    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("\n\nStopped by user")

elif choice == "5":
    print("\n" + "=" * 80)
    print("CLOUDWATCH LOGS CONSOLE")
    print("=" * 80)
    
    # URL encode the log group name
    import urllib.parse
    encoded_log_group = urllib.parse.quote(log_group)
    
    console_url = (
        f"https://console.aws.amazon.com/cloudwatch/home?"
        f"region={region}#logsV2:log-groups/log-group/{encoded_log_group}"
    )
    
    print(f"\nCloudWatch Logs Console URL:")
    print(console_url)
    print("\nCopy and paste this URL into your browser to view logs in AWS Console.")

elif choice == "6":
    print("\n" + "=" * 80)
    print("GENAI OBSERVABILITY DASHBOARD")
    print("=" * 80)
    
    dashboard_url = (
        f"https://console.aws.amazon.com/cloudwatch/home?"
        f"region={region}#gen-ai-observability/agent-core"
    )
    
    print(f"\nGenAI Observability Dashboard URL:")
    print(dashboard_url)
    print("\nThis dashboard shows:")
    print("  • Request count and success rate")
    print("  • Latency metrics (p50, p90, p99)")
    print("  • Token usage and costs")
    print("  • Error rates and types")
    print("  • Tool invocation statistics")
    print("\nCopy and paste this URL into your browser.")

elif choice == "7":
    print("\n" + "=" * 80)
    print("X-RAY TRACE INFORMATION")
    print("=" * 80)
    
    xray_url = (
        f"https://console.aws.amazon.com/xray/home?"
        f"region={region}#/service-map"
    )
    
    print(f"\nX-Ray Service Map URL:")
    print(xray_url)
    print("\nX-Ray provides:")
    print("  • Distributed tracing of requests")
    print("  • Service dependency map")
    print("  • Performance bottleneck identification")
    print("  • Error and fault analysis")
    print("\nTo filter for your agent:")
    print(f"  1. Open the URL above")
    print(f"  2. Look for service: {agent_name}")
    print(f"  3. Click on traces to see detailed flow")
    print("\nCopy and paste this URL into your browser.")

elif choice == "8":
    print("\nExiting...")
    exit(0)

else:
    print("\n❌ Invalid option. Please run the script again and select 1-8.")
    exit(1)

print("\n" + "=" * 80)
print("ADDITIONAL MONITORING COMMANDS")
print("=" * 80)
print(f"""
View logs with AWS CLI:
  aws logs tail {log_group} --follow --region {region}

View specific time range:
  aws logs tail {log_group} --since 2h --region {region}

Filter logs by pattern:
  aws logs filter-log-events \\
    --log-group-name {log_group} \\
    --filter-pattern "ERROR" \\
    --region {region}

Get log streams:
  aws logs describe-log-streams \\
    --log-group-name {log_group} \\
    --region {region}

CloudWatch Insights query:
  aws logs start-query \\
    --log-group-name {log_group} \\
    --start-time $(date -d '1 hour ago' +%s) \\
    --end-time $(date +%s) \\
    --query-string 'fields @timestamp, @message | sort @timestamp desc | limit 20' \\
    --region {region}
""")

print("=" * 80)
