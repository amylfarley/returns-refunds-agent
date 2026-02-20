# AgentCore Runtime Monitoring Guide

Complete guide for monitoring your deployed Returns & Refunds Agent.

## Quick Start

Get log information and AWS CLI commands:
```bash
python3 23_get_logs_info.py
```

Run the interactive monitoring dashboard:
```bash
python3 22_monitor_agent.py
```

---

## 1. CloudWatch Logs

### View Recent Logs (Last Hour)
```bash
aws logs tail /aws/bedrock-agentcore/runtimes/returns_refunds_agent-xRyDzcDbNQ-DEFAULT \
  --since 1h \
  --region us-west-2
```

### Tail Logs in Real-Time
```bash
aws logs tail /aws/bedrock-agentcore/runtimes/returns_refunds_agent-xRyDzcDbNQ-DEFAULT \
  --follow \
  --region us-west-2
```

### View Logs from Specific Time Range
```bash
# Last 10 minutes
aws logs tail /aws/bedrock-agentcore/runtimes/returns_refunds_agent-xRyDzcDbNQ-DEFAULT \
  --since 10m \
  --region us-west-2

# Last 24 hours
aws logs tail /aws/bedrock-agentcore/runtimes/returns_refunds_agent-xRyDzcDbNQ-DEFAULT \
  --since 24h \
  --region us-west-2

# Specific date/time
aws logs tail /aws/bedrock-agentcore/runtimes/returns_refunds_agent-xRyDzcDbNQ-DEFAULT \
  --since 2026-02-20T20:00:00 \
  --region us-west-2
```

### Filter Logs by Pattern
```bash
# Find errors
aws logs filter-log-events \
  --log-group-name /aws/bedrock-agentcore/runtimes/returns_refunds_agent-xRyDzcDbNQ-DEFAULT \
  --filter-pattern "ERROR" \
  --region us-west-2

# Find specific tool invocations
aws logs filter-log-events \
  --log-group-name /aws/bedrock-agentcore/runtimes/returns_refunds_agent-xRyDzcDbNQ-DEFAULT \
  --filter-pattern "lookup_order" \
  --region us-west-2

# Find memory operations
aws logs filter-log-events \
  --log-group-name /aws/bedrock-agentcore/runtimes/returns_refunds_agent-xRyDzcDbNQ-DEFAULT \
  --filter-pattern "Memory" \
  --region us-west-2
```

### CloudWatch Logs Console
Open in browser:
```
https://console.aws.amazon.com/cloudwatch/home?region=us-west-2#logsV2:log-groups/log-group/$252Faws$252Fbedrock-agentcore$252Fruntimes$252Freturns_refunds_agent-xRyDzcDbNQ-DEFAULT
```

---

## 2. GenAI Observability Dashboard

### Access Dashboard
Open in browser:
```
https://console.aws.amazon.com/cloudwatch/home?region=us-west-2#gen-ai-observability/agent-core
```

### What You'll See
- **Request Metrics**
  - Total requests
  - Success rate
  - Error rate
  - Requests per minute

- **Latency Metrics**
  - p50 (median)
  - p90 (90th percentile)
  - p99 (99th percentile)
  - Average response time

- **Token Usage**
  - Input tokens
  - Output tokens
  - Total tokens
  - Cost estimation

- **Tool Invocations**
  - Tool call frequency
  - Tool success rate
  - Tool latency

- **Error Analysis**
  - Error types
  - Error frequency
  - Error trends

---

## 3. X-Ray Distributed Tracing

### Access X-Ray Console
Open in browser:
```
https://console.aws.amazon.com/xray/home?region=us-west-2#/service-map
```

### View Traces
```bash
# Get recent traces
aws xray get-trace-summaries \
  --start-time $(date -d '1 hour ago' +%s) \
  --end-time $(date +%s) \
  --region us-west-2

# Get specific trace details
aws xray batch-get-traces \
  --trace-ids <trace-id> \
  --region us-west-2
```

### What X-Ray Shows
- **Service Map**: Visual representation of service dependencies
- **Traces**: Complete request flow through all services
- **Segments**: Individual service calls (Memory, Gateway, Lambda, KB)
- **Subsegments**: Detailed operations within each service
- **Annotations**: Custom metadata for filtering
- **Metadata**: Additional context about requests

---

## 4. CloudWatch Insights Queries

### Run Insights Query
```bash
aws logs start-query \
  --log-group-name /aws/bedrock-agentcore/runtimes/returns_refunds_agent-xRyDzcDbNQ-DEFAULT \
  --start-time $(date -d '1 hour ago' +%s) \
  --end-time $(date +%s) \
  --query-string 'fields @timestamp, @message | sort @timestamp desc | limit 20' \
  --region us-west-2
```

### Useful Queries

**Find Slowest Requests**
```
fields @timestamp, @message
| filter @message like /duration/
| parse @message /duration: (?<duration>\d+)/
| sort duration desc
| limit 10
```

**Count Errors by Type**
```
fields @timestamp, @message
| filter @message like /ERROR/
| stats count() by @message
```

**Track Tool Usage**
```
fields @timestamp, @message
| filter @message like /tool/
| parse @message /tool: (?<tool_name>\w+)/
| stats count() by tool_name
```

**Monitor Response Times**
```
fields @timestamp, @message
| filter @message like /response_time/
| parse @message /response_time: (?<time>\d+)/
| stats avg(time), max(time), min(time)
```

---

## 5. Monitoring Scripts

### Get Log Information
```bash
python3 23_get_logs_info.py
```

This script displays:
- Agent ARN and details
- CloudWatch log group name
- CloudWatch Console URL
- 8 AWS CLI commands for log access
- GenAI Dashboard URL
- X-Ray Service Map URL

### Interactive Monitoring Dashboard
```bash
python3 22_monitor_agent.py
```

Options:
1. **View Recent Logs** - Last hour of logs
2. **Filter Logs by Pattern** - Search for specific text
3. **Get GenAI Dashboard URL** - Open observability dashboard
4. **View X-Ray Traces** - Distributed tracing information
5. **Check Agent Status** - Current deployment status
6. **Get Log Statistics** - Log volume and patterns
7. **Tail Logs in Real-Time** - Follow mode for live logs

The interactive dashboard provides:
- Easy access to all monitoring features
- No need to remember complex AWS CLI commands
- Quick troubleshooting and debugging
- Real-time log viewing

---

## 6. Metrics and Alarms

### Create CloudWatch Alarm for Errors
```bash
aws cloudwatch put-metric-alarm \
  --alarm-name returns-agent-errors \
  --alarm-description "Alert on agent errors" \
  --metric-name Errors \
  --namespace AWS/BedrockAgentCore \
  --statistic Sum \
  --period 300 \
  --threshold 5 \
  --comparison-operator GreaterThanThreshold \
  --evaluation-periods 1 \
  --region us-west-2
```

### Create Alarm for High Latency
```bash
aws cloudwatch put-metric-alarm \
  --alarm-name returns-agent-latency \
  --alarm-description "Alert on high latency" \
  --metric-name Duration \
  --namespace AWS/BedrockAgentCore \
  --statistic Average \
  --period 300 \
  --threshold 5000 \
  --comparison-operator GreaterThanThreshold \
  --evaluation-periods 2 \
  --region us-west-2
```

---

## 7. Log Analysis Tips

### What to Look For

**Successful Invocations**
- Look for: "AGENT INVOCATION STARTED"
- Look for: "Agent response generated successfully"
- Status: 200 responses

**Memory Operations**
- Look for: "Memory configured"
- Look for: "Memory session manager configured"
- Check: Memory retrieval results

**Gateway Operations**
- Look for: "Gateway configured"
- Look for: "Gateway tools loaded"
- Check: Tool invocation results

**Errors**
- Look for: "ERROR", "FAILED", "Exception"
- Check: Stack traces
- Review: Error messages

**Performance**
- Look for: Response times
- Check: Token usage
- Monitor: Tool execution times

---

## 8. Troubleshooting Common Issues

### Agent Not Responding
```bash
# Check agent status
python3 20_check_status.py

# View recent errors
aws logs tail /aws/bedrock-agentcore/runtimes/returns_refunds_agent-xRyDzcDbNQ-DEFAULT \
  --since 10m \
  --filter-pattern "ERROR" \
  --region us-west-2
```

### High Latency
```bash
# Check X-Ray traces for bottlenecks
# Look for slow segments in service map
# Review tool execution times in logs
```

### Memory Issues
```bash
# Check memory retrieval logs
aws logs filter-log-events \
  --log-group-name /aws/bedrock-agentcore/runtimes/returns_refunds_agent-xRyDzcDbNQ-DEFAULT \
  --filter-pattern "Memory" \
  --region us-west-2
```

### Gateway Issues
```bash
# Check gateway authentication
aws logs filter-log-events \
  --log-group-name /aws/bedrock-agentcore/runtimes/returns_refunds_agent-xRyDzcDbNQ-DEFAULT \
  --filter-pattern "Gateway" \
  --region us-west-2
```

---

## 9. Best Practices

### Regular Monitoring
- Check logs daily for errors
- Review GenAI dashboard weekly
- Monitor token usage for cost optimization
- Set up alarms for critical metrics

### Performance Optimization
- Identify slow tool invocations
- Optimize memory retrieval queries
- Cache frequently accessed data
- Monitor and optimize token usage

### Cost Management
- Track token usage trends
- Monitor request volume
- Optimize prompt engineering
- Review and adjust memory retention

### Security
- Monitor for authentication failures
- Review access patterns
- Check for unusual activity
- Audit IAM role usage

---

## 10. Quick Reference

### Log Group Name
```
/aws/bedrock-agentcore/runtimes/returns_refunds_agent-xRyDzcDbNQ-DEFAULT
```

### Agent ARN
```
arn:aws:bedrock-agentcore:us-west-2:652492146510:runtime/returns_refunds_agent-xRyDzcDbNQ
```

### Region
```
us-west-2
```

### Useful Commands
```bash
# Get log info and commands
python3 23_get_logs_info.py

# Interactive monitoring
python3 22_monitor_agent.py

# Quick log view
aws logs tail <log-group> --since 1h --region us-west-2

# Follow logs
aws logs tail <log-group> --follow --region us-west-2

# Filter errors
aws logs filter-log-events --log-group-name <log-group> --filter-pattern "ERROR" --region us-west-2

# Check status
python3 20_check_status.py
```

---

## 11. Monitoring Workflow

### Daily Monitoring Routine
1. Run `python3 22_monitor_agent.py` - Check recent logs (Option 1)
2. Review GenAI Dashboard (Option 3) - Check metrics and trends
3. Look for errors or warnings in logs
4. Verify response times are acceptable

### Weekly Review
1. Analyze token usage trends in GenAI Dashboard
2. Review X-Ray traces for performance bottlenecks
3. Check CloudWatch Insights for patterns
4. Review and adjust alarms if needed

### Troubleshooting Workflow
1. Run `python3 23_get_logs_info.py` - Get log group details
2. Run `python3 22_monitor_agent.py` - Use interactive dashboard
3. Filter logs by error pattern (Option 2)
4. Check X-Ray traces for failed requests (Option 4)
5. Review agent status (Option 5)
6. Tail logs in real-time if issue is ongoing (Option 7)

---

**Last Updated**: 2026-02-20  
**Agent Version**: 3.1  
**Status**: Production-Ready ✅  
**Total Monitoring Scripts**: 2 (22_monitor_agent.py, 23_get_logs_info.py)
