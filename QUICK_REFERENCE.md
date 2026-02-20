# Quick Reference Card

Essential commands and information for working with the Returns & Refunds Agent.

## 🚀 Quick Commands

### Setup
```bash
# Clone and setup
git clone https://github.com/YOUR_USERNAME/returns-refunds-agent.git
cd returns-refunds-agent
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Deploy Infrastructure (in order)
```bash
python3 03_create_memory.py          # Create memory
python3 04_seed_memory.py            # Seed with sample data
python3 08_create_cognito.py         # Setup authentication
python3 09_create_gateway_role.py    # Create IAM role
python3 10_create_lambda.py          # Create Lambda function
python3 11_create_gateway.py         # Create gateway
python3 12_add_lambda_to_gateway.py  # Register Lambda target
```

### Deploy to Runtime (Production)
```bash
python3 16_create_runtime_role.py    # Create runtime IAM role
python3 19_deploy_agent.py           # Deploy to AgentCore Runtime (5-10 min)
python3 20_check_status.py           # Monitor deployment status
python3 21_invoke_agent.py           # Test production agent
```

### Monitoring
```bash
python3 22_monitor_agent.py          # Interactive monitoring dashboard
python3 23_get_logs_info.py          # Get CloudWatch logs info
```

### Test
```bash
python3 02_test_agent.py             # Test basic agent
python3 07_test_memory_agent.py      # Test memory integration
python3 15_test_full_agent.py        # Test complete system
```

### Verify
```bash
python3 05_test_memory.py            # Check memory retrieval
python3 13_list_gateway_targets.py   # List gateway targets
```

## 📁 Key Files

| File | Purpose |
|------|---------|
| `17_runtime_agent.py` | Production runtime agent (with @app.entrypoint) |
| `14_full_agent.py` | Complete local agent with all features |
| `01_returns_refunds_agent.py` | Basic agent with KB only |
| `06_memory_enabled_agent.py` | Agent with memory integration |
| `22_monitor_agent.py` | Interactive monitoring dashboard |
| `23_get_logs_info.py` | CloudWatch logs information |

## 🔧 Configuration Files (Auto-Generated)

| File | Contains | Sensitive? |
|------|----------|------------|
| `kb_config.json` | Knowledge Base ID | No |
| `memory_config.json` | Memory resource ID | No |
| `cognito_config.json` | Auth credentials | ⚠️ YES |
| `gateway_config.json` | Gateway URL/ID | No |
| `lambda_config.json` | Lambda ARN | No |
| `gateway_role_config.json` | Gateway IAM role ARN | No |
| `runtime_execution_role_config.json` | Runtime IAM role ARN | No |
| `runtime_config.json` | Agent ARN | No |

**Note**: Sensitive files are excluded from Git via `.gitignore`.

## 🛠️ Custom Tools

```python
# Check return eligibility
check_return_eligibility(
    purchase_date="2024-01-15",  # YYYY-MM-DD
    category="electronics"        # electronics, clothing, etc.
)

# Calculate refund
calculate_refund_amount(
    original_price=1299.99,
    condition="new",              # new, opened, used, damaged
    return_reason="defective"     # defective, wrong_item, changed_mind
)

# Format policy text
format_policy_response(
    policy_text="...",
    customer_question="..."
)
```

## 🧠 Memory Namespaces

| Namespace | Purpose | Example |
|-----------|---------|---------|
| `app/{actorId}/semantic` | Factual details | "Purchased laptop on 2024-01-15" |
| `app/{actorId}/preferences` | User preferences | "Prefers email notifications" |
| `app/{actorId}/{sessionId}/summary` | Conversation summaries | "Discussed return policy" |

## 🔐 Authentication Flow

```python
# 1. Get OAuth token
token = get_cognito_token_with_scope(
    client_id, client_secret, discovery_url,
    scope="gateway-api/read gateway-api/write"
)

# 2. Use token with gateway
headers = {"Authorization": f"Bearer {token}"}
```

## 📊 AWS Resources

| Resource | Name/ID | Region |
|----------|---------|--------|
| Memory | returns_refunds_memory-p7dffNC0ha | us-west-2 |
| Knowledge Base | XWCNYZDEGT | us-west-2 |
| Lambda | OrderLookupFunction | us-west-2 |
| Gateway | returnsrefundsgateway-q6skfjrtth | us-west-2 |
| Cognito Pool | us-west-2_jblrQsfU3 | us-west-2 |
| Runtime Agent | returns_refunds_agent-xRyDzcDbNQ | us-west-2 |
| Model | claude-sonnet-4-5 | us-west-2 |

## 🧪 Test Queries

```python
# Memory test
"Hi! What do you remember about my preferences?"

# Order lookup test
"Look up order ORD-001"

# Eligibility test
"Can I return a laptop purchased 25 days ago?"

# Refund calculation test
"Calculate refund for $500 item in like-new condition"

# Full integration test
"Look up order ORD-001 and check if I can return it. I prefer email."
```

## 📦 Mock Data

### Lambda Orders
- **ORD-001**: Dell XPS 15 Laptop, $1,299.99, purchased 2024-02-05 (eligible)
- **ORD-002**: iPhone 14 Pro, $999.99, purchased 2023-12-01 (not eligible)
- **ORD-003**: iPad Air, $599.99, purchased 2024-02-10 (eligible)

### Memory Seed Data (user_001)
- Preference: Email notifications
- History: Returned defective laptop previously

## 🔍 Debugging

### Check AWS Resources
```bash
# Memory status
aws bedrock-agentcore-control get-memory \
  --memory-id $(jq -r .memory_id memory_config.json) \
  --region us-west-2

# Gateway status
aws bedrock-agentcore-control get-gateway \
  --gateway-identifier $(jq -r .gateway_id gateway_config.json) \
  --region us-west-2

# Lambda status
aws lambda get-function \
  --function-name OrderLookupFunction \
  --region us-west-2

# Runtime agent status
python3 20_check_status.py
```

### View Logs
```bash
# Interactive monitoring
python3 22_monitor_agent.py

# Get log group info
python3 23_get_logs_info.py

# Tail logs in real-time
aws logs tail /aws/bedrock-agentcore/runtimes/returns_refunds_agent-xRyDzcDbNQ-DEFAULT \
  --follow --region us-west-2

# View recent logs (last hour)
aws logs tail /aws/bedrock-agentcore/runtimes/returns_refunds_agent-xRyDzcDbNQ-DEFAULT \
  --since 1h --region us-west-2

# Filter for errors
aws logs filter-log-events \
  --log-group-name /aws/bedrock-agentcore/runtimes/returns_refunds_agent-xRyDzcDbNQ-DEFAULT \
  --filter-pattern "ERROR" \
  --region us-west-2
```

### Observability Dashboards
```bash
# GenAI Observability Dashboard
https://console.aws.amazon.com/cloudwatch/home?region=us-west-2#gen-ai-observability/agent-core

# X-Ray Service Map
https://console.aws.amazon.com/xray/home?region=us-west-2#/service-map

# CloudWatch Logs
https://console.aws.amazon.com/cloudwatch/home?region=us-west-2#logsV2:log-groups
```

### Common Issues

| Issue | Solution |
|-------|----------|
| "Memory not found" | Run `03_create_memory.py` |
| "Gateway authentication failed" | Check `cognito_config.json` credentials |
| "Lambda not found" | Run `10_create_lambda.py` |
| "Target not ready" | Wait 30 seconds, check with `13_list_gateway_targets.py` |
| "Runtime deployment failed" | Check `20_check_status.py` for error details |
| "Agent not responding" | Check CloudWatch logs with `22_monitor_agent.py` |
| "No logs visible" | Wait 1-2 minutes after invocation, then check again |

## 📚 Documentation

- [README.md](README.md) - Complete project documentation
- [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md) - Step-by-step deployment
- [MONITORING_GUIDE.md](MONITORING_GUIDE.md) - Monitoring and observability
- [GITHUB_SETUP.md](GITHUB_SETUP.md) - GitHub repository setup
- [architecture_visual.md](architecture_visual.md) - Architecture diagrams
- [arch_diagram.md](arch_diagram.md) - Technical specifications

## 🎯 Agent Capabilities

| Capability | Status | Script |
|------------|--------|--------|
| Memory Recall | ✅ | 07_test_memory_agent.py |
| Order Lookup | ✅ | 15_test_full_agent.py |
| Return Eligibility | ✅ | 02_test_agent.py |
| Refund Calculation | ✅ | 02_test_agent.py |
| Policy Retrieval | ✅ | 02_test_agent.py |
| OAuth Authentication | ✅ | 15_test_full_agent.py |
| Runtime Deployment | ✅ | 21_invoke_agent.py |
| CloudWatch Monitoring | ✅ | 22_monitor_agent.py |

## 💡 Tips

1. **Always activate venv**: `source .venv/bin/activate`
2. **Run scripts in order**: Follow the numbered sequence (03, 04, 08, 09, 10, 11, 12, 16, 19)
3. **Wait for memory**: After seeding, wait 30 seconds for processing
4. **Check configs**: Verify JSON files are created after each script
5. **Test incrementally**: Test after each major component (memory, gateway, full, runtime)
6. **Monitor deployment**: Use `20_check_status.py` to track runtime deployment progress
7. **Use monitoring tools**: `22_monitor_agent.py` provides interactive dashboard for logs
8. **Check logs regularly**: CloudWatch logs help troubleshoot issues quickly

## 🔗 Useful Links

- [Strands Agents Docs](https://strandsagents.com)
- [AgentCore Docs](https://aws.github.io/bedrock-agentcore-starter-toolkit/)
- [AWS Bedrock](https://aws.amazon.com/bedrock/)
- [Amazon Cognito](https://aws.amazon.com/cognito/)

---

**Quick Start**: See [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md)  
**Monitoring**: See [MONITORING_GUIDE.md](MONITORING_GUIDE.md)  
**GitHub Setup**: See [GITHUB_SETUP.md](GITHUB_SETUP.md)  
**Full Docs**: See [README.md](README.md)  
**Total Scripts**: 22 Python scripts
