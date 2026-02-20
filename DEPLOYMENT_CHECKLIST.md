# Deployment Checklist

Use this checklist to deploy the Returns & Refunds Agent from scratch.

## ✅ Prerequisites

- [ ] AWS Account with appropriate permissions
- [ ] AWS CLI configured (`aws configure`)
- [ ] Python 3.10+ installed
- [ ] Access to Amazon Bedrock models (Claude Sonnet 4.5)
- [ ] Knowledge Base already created (CloudFormation stack 'knowledgebase')

## ✅ Environment Setup

- [ ] Clone repository
- [ ] Create virtual environment: `python -m venv .venv`
- [ ] Activate virtual environment: `source .venv/bin/activate`
- [ ] Install dependencies: `pip install -r requirements.txt`

## ✅ Infrastructure Deployment (Run in Order)

### Step 1: Memory Setup
- [ ] Run: `python3 03_create_memory.py`
- [ ] Verify: `memory_config.json` created with memory_id
- [ ] Run: `python3 04_seed_memory.py`
- [ ] Wait: 30 seconds for memory processing
- [ ] Test: `python3 05_test_memory.py`
- [ ] Verify: Memory retrieval shows preferences

### Step 2: Authentication Setup
- [ ] Run: `python3 08_create_cognito.py`
- [ ] Verify: `cognito_config.json` created with credentials
- [ ] Note: User Pool ID, Client ID, Client Secret saved

### Step 3: IAM Role Setup
- [ ] Run: `python3 09_create_gateway_role.py`
- [ ] Verify: `gateway_role_config.json` created with role ARN
- [ ] Note: Role has Lambda invoke permissions

### Step 4: Lambda Function Setup
- [ ] Run: `python3 10_create_lambda.py`
- [ ] Verify: `lambda_config.json` created with function ARN
- [ ] Note: Function has 3 mock orders (ORD-001, ORD-002, ORD-003)

### Step 5: Gateway Setup
- [ ] Run: `python3 11_create_gateway.py`
- [ ] Verify: `gateway_config.json` created with gateway URL
- [ ] Note: Gateway ID and URL saved

### Step 6: Gateway Target Registration
- [ ] Run: `python3 12_add_lambda_to_gateway.py`
- [ ] Verify: Target added successfully
- [ ] Test: `python3 13_list_gateway_targets.py`
- [ ] Verify: OrderLookup target shows status READY

## ✅ Testing

### Basic Agent Test
- [ ] Run: `python3 02_test_agent.py`
- [ ] Verify: Agent responds to queries
- [ ] Verify: Custom tools work (eligibility, refund calculation)

### Memory-Enabled Agent Test
- [ ] Run: `python3 07_test_memory_agent.py`
- [ ] Verify: Agent recalls user preferences
- [ ] Verify: Memory integration working

### Full System Test
- [ ] Run: `python3 15_test_full_agent.py`
- [ ] Verify: ✅ Memory recall (email preference)
- [ ] Verify: ✅ Gateway integration (order lookup)
- [ ] Verify: ✅ Lambda invocation (order details)
- [ ] Verify: ✅ Custom tools (eligibility calculation)
- [ ] Verify: ✅ Personalized response

## ✅ Configuration Files Generated

After successful deployment, you should have:

- [ ] `kb_config.json` - Knowledge Base ID
- [ ] `memory_config.json` - Memory resource ID
- [ ] `cognito_config.json` - Authentication credentials
- [ ] `gateway_role_config.json` - IAM role ARN
- [ ] `lambda_config.json` - Lambda function details
- [ ] `gateway_config.json` - Gateway endpoint

**⚠️ SECURITY**: These files contain sensitive information and are excluded from Git via `.gitignore`.

## ✅ Verification

### Resource Status Check

```bash
# Check Memory
aws bedrock-agentcore-control get-memory \
  --memory-id $(jq -r .memory_id memory_config.json) \
  --region us-west-2

# Check Gateway
aws bedrock-agentcore-control get-gateway \
  --gateway-identifier $(jq -r .gateway_id gateway_config.json) \
  --region us-west-2

# Check Lambda
aws lambda get-function \
  --function-name OrderLookupFunction \
  --region us-west-2

# Check Cognito
aws cognito-idp describe-user-pool \
  --user-pool-id $(jq -r .user_pool_id cognito_config.json) \
  --region us-west-2
```

### End-to-End Test

```bash
python3 15_test_full_agent.py
```

Expected output should show:
- Memory recall of email preference
- Order lookup via gateway (ORD-001)
- Return eligibility calculation (15 days remaining)
- Personalized response combining all data

## ✅ Cleanup (Optional)

To remove all deployed resources:

```bash
# Delete Gateway Target
python3 -c "
import boto3, json
with open('gateway_config.json') as f:
    gw = json.load(f)
with open('lambda_config.json') as f:
    lam = json.load(f)
client = boto3.client('bedrock-agentcore-control', region_name='us-west-2')
targets = client.list_gateway_targets(gatewayIdentifier=gw['gateway_id'])
for t in targets['gatewayTargets']:
    client.delete_gateway_target(gatewayIdentifier=gw['gateway_id'], targetId=t['targetId'])
"

# Delete Gateway
python3 -c "
import boto3, json
with open('gateway_config.json') as f:
    gw = json.load(f)
client = boto3.client('bedrock-agentcore-control', region_name='us-west-2')
client.delete_gateway(gatewayIdentifier=gw['gateway_id'])
"

# Delete Lambda
aws lambda delete-function --function-name OrderLookupFunction --region us-west-2

# Delete IAM Role
python3 -c "
import boto3, json
with open('gateway_role_config.json') as f:
    role = json.load(f)
role_name = role['role_arn'].split('/')[-1]
iam = boto3.client('iam')
# Detach policies first
policies = iam.list_attached_role_policies(RoleName=role_name)
for p in policies['AttachedPolicies']:
    iam.detach_role_policy(RoleName=role_name, PolicyArn=p['PolicyArn'])
    iam.delete_policy(PolicyArn=p['PolicyArn'])
iam.delete_role(RoleName=role_name)
"

# Delete Memory
python3 -c "
import boto3, json
from bedrock_agentcore_starter_toolkit.operations.memory.manager import MemoryManager
with open('memory_config.json') as f:
    mem = json.load(f)
manager = MemoryManager(region_name='us-west-2')
manager.delete_memory(memory_id=mem['memory_id'])
"

# Delete Cognito
python3 -c "
import boto3, json
with open('cognito_config.json') as f:
    cog = json.load(f)
client = boto3.client('cognito-idp', region_name='us-west-2')
client.delete_user_pool_domain(Domain=cog['domain_prefix'], UserPoolId=cog['user_pool_id'])
client.delete_user_pool(UserPoolId=cog['user_pool_id'])
"

# Remove config files
rm -f memory_config.json cognito_config.json gateway_role_config.json
rm -f lambda_config.json gateway_config.json
```

## 📊 Deployment Summary

| Component | Script | Config File | Status |
|-----------|--------|-------------|--------|
| Memory | 03_create_memory.py | memory_config.json | ⬜ |
| Memory Seed | 04_seed_memory.py | - | ⬜ |
| Cognito | 08_create_cognito.py | cognito_config.json | ⬜ |
| IAM Role | 09_create_gateway_role.py | gateway_role_config.json | ⬜ |
| Lambda | 10_create_lambda.py | lambda_config.json | ⬜ |
| Gateway | 11_create_gateway.py | gateway_config.json | ⬜ |
| Gateway Target | 12_add_lambda_to_gateway.py | - | ⬜ |

## 🎯 Success Criteria

Deployment is successful when:

1. ✅ All 6 configuration files are created
2. ✅ Memory test shows preference recall
3. ✅ Gateway target shows READY status
4. ✅ Full agent test passes all verifications
5. ✅ No errors in any deployment script

---

**Estimated Deployment Time**: 10-15 minutes  
**Region**: us-west-2  
**Cost**: Minimal (mostly serverless, pay-per-use)
