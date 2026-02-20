# Returns & Refunds Agent - Complete AgentCore Implementation

A production-ready AI agent built with AWS Bedrock AgentCore, featuring memory, gateway integration, and knowledge base access for intelligent customer service.

**🚀 Status**: Deployed to AgentCore Runtime & Production-Ready  
**📦 Total Scripts**: 20 Python scripts  
**✅ Verified**: All integrations tested in production

## 🎯 Overview

This project demonstrates a complete implementation of an AI-powered returns and refunds assistant using:

- **Strands Agents SDK** - Agent framework
- **AgentCore Memory** - Customer preference and history storage
- **AgentCore Gateway** - Tool integration via MCP protocol
- **AWS Lambda** - Order lookup functionality
- **Bedrock Knowledge Base** - Policy document retrieval
- **Amazon Cognito** - OAuth2 authentication

## ✨ Features

- 🧠 **Memory Integration** - Remembers customer preferences across sessions
- 🔍 **Order Lookup** - Retrieves order details via Lambda through Gateway
- 📚 **Policy Access** - Searches knowledge base for return policies
- 🛠️ **Custom Tools** - Return eligibility checking and refund calculation
- 🔐 **Secure Authentication** - OAuth2 client credentials flow
- 🎨 **Personalized Responses** - Combines memory, data, and policies

## 🏗️ Architecture

```
Customer → Strands Agent → Memory Service
                        → Gateway (MCP) → Lambda (Order Lookup)
                        → Knowledge Base (Policies)
                        → Custom Tools (Eligibility, Refunds)
```

See [architecture_visual.md](architecture_visual.md) for detailed diagrams.

## 📋 Prerequisites

- AWS Account with appropriate permissions
- Python 3.10 or newer
- AWS CLI configured (`aws configure`)
- Access to Amazon Bedrock models (Claude Sonnet 4.5)

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/amylfarley/returns-refunds-agent.git
cd returns-refunds-agent
```

### 2. Set Up Python Environment

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Deploy Infrastructure (Run scripts in order)

```bash
# Memory Setup
python3 03_create_memory.py          # Create memory resource
python3 04_seed_memory.py            # Seed with sample data

# Authentication Setup
python3 08_create_cognito.py         # Create Cognito User Pool

# Gateway Setup
python3 09_create_gateway_role.py    # Create IAM role for Gateway
python3 10_create_lambda.py          # Create Lambda function
python3 11_create_gateway.py         # Create Gateway
python3 12_add_lambda_to_gateway.py  # Register Lambda target

# Runtime Deployment
python3 16_create_runtime_role.py    # Create Runtime execution role
python3 19_deploy_agent.py           # Deploy to AgentCore Runtime (5-10 min)
python3 20_check_status.py           # Monitor deployment status
```

### 4. Test the Agent

```bash
# Test locally
python3 15_test_full_agent.py        # Test complete local system

# Test production runtime
python3 21_invoke_agent.py           # Invoke deployed runtime agent
```

## 📁 Project Structure

```
.
├── README.md                          # This file
├── requirements.txt                   # Local development dependencies
├── requirements_runtime.txt           # Runtime deployment dependencies
├── .gitignore                         # Git ignore rules
├── architecture_visual.md             # Visual architecture diagrams
├── arch_diagram.md                    # Detailed architecture documentation
│
├── Agent Files (4 scripts)
│   ├── 01_returns_refunds_agent.py    # Basic agent with KB
│   ├── 06_memory_enabled_agent.py     # Agent with memory
│   ├── 14_full_agent.py               # Complete local agent
│   └── 17_runtime_agent.py            # Production runtime agent ⭐
│
├── Infrastructure Scripts (9 scripts)
│   ├── 03_create_memory.py            # Create AgentCore Memory
│   ├── 04_seed_memory.py              # Seed memory with data
│   ├── 08_create_cognito.py           # Setup Cognito authentication
│   ├── 09_create_gateway_role.py      # Create Gateway IAM role
│   ├── 10_create_lambda.py            # Create Lambda function
│   ├── 11_create_gateway.py           # Create Gateway
│   ├── 12_add_lambda_to_gateway.py    # Register Lambda target
│   ├── 16_create_runtime_role.py      # Create Runtime IAM role ⭐
│   └── 19_deploy_agent.py             # Deploy to Runtime ⭐
│
├── Test Scripts (7 scripts)
│   ├── 02_test_agent.py               # Test basic agent
│   ├── 05_test_memory.py              # Test memory retrieval
│   ├── 07_test_memory_agent.py        # Test memory-enabled agent
│   ├── 13_list_gateway_targets.py     # List gateway targets
│   ├── 15_test_full_agent.py          # Local end-to-end test
│   ├── 20_check_status.py             # Monitor deployment ⭐
│   └── 21_invoke_agent.py             # Invoke runtime agent ⭐
│
├── Documentation
│   ├── DEPLOYMENT_CHECKLIST.md        # Step-by-step deployment
│   ├── QUICK_REFERENCE.md             # Quick commands
│   ├── GITHUB_SETUP.md                # GitHub setup guide
│   └── PUSH_TO_GITHUB.md              # Git push instructions
│
└── Configuration Files (Generated)
    ├── kb_config.json                 # Knowledge Base ID
    ├── memory_config.json             # Memory ID
    ├── cognito_config.json            # Cognito credentials
    ├── gateway_role_config.json       # Gateway IAM role
    ├── lambda_config.json             # Lambda ARN and schema
    ├── gateway_config.json            # Gateway URL and ID
    ├── runtime_execution_role_config.json  # Runtime IAM role ⭐
    └── runtime_config.json            # Agent ARN ⭐

⭐ = New for Runtime Deployment
Total: 20 Python scripts
```

## 🔧 Configuration

All configuration is automatically saved to JSON files during deployment. The agent loads these files at runtime.

### Required Configuration Files

- `kb_config.json` - Knowledge Base ID (from CloudFormation)
- `memory_config.json` - Memory resource ID
- `cognito_config.json` - Authentication credentials
- `gateway_config.json` - Gateway endpoint
- `lambda_config.json` - Lambda function details

## 🧪 Testing

### Test Memory Integration

```bash
python3 07_test_memory_agent.py
```

Expected: Agent recalls customer preferences from seeded memory.

### Test Complete System

```bash
python3 15_test_full_agent.py
```

Expected: Agent demonstrates:
- ✅ Memory recall (email preference)
- ✅ Order lookup (ORD-001 via Lambda)
- ✅ Return eligibility calculation
- ✅ Personalized response

## 📊 Verification Results

### Local Testing
**Test Date**: 2026-02-20  
**Test Script**: 15_test_full_agent.py  
**Status**: ✅ ALL CAPABILITIES VERIFIED

| Capability | Status | Evidence |
|------------|--------|----------|
| Memory Integration | ✅ PASS | Recalled email preference |
| Gateway Integration | ✅ PASS | Retrieved order ORD-001 |
| Lambda Invocation | ✅ PASS | Got order details |
| Custom Tools | ✅ PASS | Calculated eligibility |
| OAuth Authentication | ✅ PASS | JWT token obtained |
| Personalization | ✅ PASS | Combined all data |

### Production Runtime Testing
**Deployment Date**: 2026-02-20  
**Test Script**: 21_invoke_agent.py  
**Status**: ✅ PRODUCTION DEPLOYMENT VERIFIED

| Metric | Value |
|--------|-------|
| Agent ARN | returns_refunds_agent-xRyDzcDbNQ |
| Deployment Status | READY ✅ |
| Build Time | 36 seconds |
| Deployment Time | 2-3 minutes |
| Response Time | < 5 seconds |
| Gateway Integration | ✅ Working |
| Memory Integration | ✅ Working |
| Custom Tools | ✅ Working |
| OAuth Authentication | ✅ Working |

## 🛠️ Custom Tools

The agent includes three custom tools:

1. **check_return_eligibility** - Validates return window based on purchase date
2. **calculate_refund_amount** - Calculates refund with condition-based deductions
3. **format_policy_response** - Formats policy info in customer-friendly way

## 🔐 Security

- OAuth2 client credentials flow for gateway authentication
- IAM roles with least privilege permissions
- JWT token validation
- Encrypted memory storage
- Namespace isolation per customer

## 🚀 AgentCore Runtime Deployment

This project includes complete deployment to AWS Bedrock AgentCore Runtime:

### Deployment Features
- **Serverless**: No infrastructure management required
- **Auto-scaling**: Handles variable load automatically
- **ARM64 Container**: Optimized for performance
- **CodeBuild Pipeline**: Automated build and deployment
- **Observability**: CloudWatch Logs + X-Ray traces built-in

### Deployment Scripts
1. **16_create_runtime_role.py** - Creates IAM execution role with all required permissions
2. **17_runtime_agent.py** - Production agent with `@app.entrypoint` decorator
3. **19_deploy_agent.py** - Deploys to runtime (builds container, pushes to ECR, deploys)
4. **20_check_status.py** - Monitors deployment until READY
5. **21_invoke_agent.py** - Tests deployed agent with OAuth authentication

### Deployment Time
- **Build**: ~36 seconds (CodeBuild)
- **Total Deployment**: 2-3 minutes
- **Status Check**: Real-time monitoring

### Production Metrics
- **Response Time**: < 5 seconds
- **Container Platform**: ARM64
- **Container Registry**: Amazon ECR
- **Observability**: CloudWatch + X-Ray enabled
- **Status**: READY ✅

## 📚 Documentation

### Project Documentation
- [Quick Reference](QUICK_REFERENCE.md) - Essential commands and information
- [Deployment Checklist](DEPLOYMENT_CHECKLIST.md) - Step-by-step deployment guide
- [GitHub Setup Guide](GITHUB_SETUP.md) - Instructions for creating GitHub repository
- [Architecture Diagrams](architecture_visual.md) - Visual system architecture
- [Technical Documentation](arch_diagram.md) - Detailed component specs

### External Resources
- [Strands Agents Docs](https://strandsagents.com) - Framework documentation
- [AgentCore Docs](https://aws.github.io/bedrock-agentcore-starter-toolkit/) - Platform documentation

## 🎓 Learning Resources

This project demonstrates:

- Building agents with Strands SDK
- Deploying to AgentCore Runtime
- Integrating AgentCore Memory for personalization
- Using Gateway for external tool access
- Lambda function integration via MCP
- Knowledge Base integration for RAG
- OAuth2 authentication flows
- Custom tool development
- Production deployment with Docker/CodeBuild
- CloudWatch observability and X-Ray tracing

## 🤝 Contributing

This is a reference implementation. Feel free to:

- Add more Lambda functions as gateway targets
- Extend custom tools
- Add more memory namespaces
- Integrate additional AWS services

## 📝 License

This project is provided as-is for educational and reference purposes.

## 🙏 Acknowledgments

Built with:
- [Strands Agents SDK](https://strandsagents.com)
- [AWS Bedrock AgentCore](https://aws.amazon.com/bedrock/)
- [Amazon Bedrock](https://aws.amazon.com/bedrock/)
- [AWS Lambda](https://aws.amazon.com/lambda/)
- [Amazon Cognito](https://aws.amazon.com/cognito/)

## 📧 Support

For issues or questions:
- Review the [architecture documentation](arch_diagram.md)
- Check the [test scripts](15_test_full_agent.py) for examples
- Consult [Strands documentation](https://strandsagents.com)

---

**Status**: ✅ Production-Ready & Deployed to AgentCore Runtime  
**Version**: 3.0  
**Last Updated**: 2026-02-20  
**Repository**: https://github.com/amylfarley/returns-refunds-agent
