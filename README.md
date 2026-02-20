# Returns & Refunds Agent - Complete AgentCore Implementation

A production-ready AI agent built with AWS Bedrock AgentCore, featuring memory, gateway integration, and knowledge base access for intelligent customer service.

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
git clone https://github.com/YOUR_USERNAME/returns-refunds-agent.git
cd returns-refunds-agent
```

**Note**: If you're setting up this repository for the first time, see [GITHUB_SETUP.md](GITHUB_SETUP.md) for detailed instructions.

### 2. Set Up Python Environment

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Deploy Infrastructure (Run scripts in order)

```bash
# Step 1: Create Memory
python3 03_create_memory.py

# Step 2: Seed Memory with sample data
python3 04_seed_memory.py

# Step 3: Create Cognito for authentication
python3 08_create_cognito.py

# Step 4: Create IAM role for Gateway
python3 09_create_gateway_role.py

# Step 5: Create Lambda function
python3 10_create_lambda.py

# Step 6: Create Gateway
python3 11_create_gateway.py

# Step 7: Add Lambda to Gateway
python3 12_add_lambda_to_gateway.py
```

### 4. Test the Agent

```bash
# Test memory integration
python3 07_test_memory_agent.py

# Test complete system
python3 15_test_full_agent.py
```

## 📁 Project Structure

```
.
├── README.md                          # This file
├── GITHUB_SETUP.md                    # GitHub repository setup guide
├── requirements.txt                   # Python dependencies
├── .gitignore                         # Git ignore rules (excludes sensitive configs)
├── architecture_visual.md             # Visual architecture diagrams
├── arch_diagram.md                    # Detailed architecture documentation
│
├── Agent Files
│   ├── 01_returns_refunds_agent.py    # Basic agent with KB
│   ├── 06_memory_enabled_agent.py     # Agent with memory
│   └── 14_full_agent.py               # Complete agent (all features)
│
├── Infrastructure Scripts
│   ├── 03_create_memory.py            # Create AgentCore Memory
│   ├── 08_create_cognito.py           # Setup Cognito authentication
│   ├── 09_create_gateway_role.py      # Create IAM role
│   ├── 10_create_lambda.py            # Create Lambda function
│   ├── 11_create_gateway.py           # Create Gateway
│   └── 12_add_lambda_to_gateway.py    # Register Lambda target
│
├── Test Scripts
│   ├── 02_test_agent.py               # Test basic agent
│   ├── 05_test_memory.py              # Test memory retrieval
│   ├── 07_test_memory_agent.py        # Test memory-enabled agent
│   ├── 13_list_gateway_targets.py     # List gateway targets
│   └── 15_test_full_agent.py          # End-to-end test
│
└── Configuration Files (Generated)
    ├── kb_config.json                 # Knowledge Base ID
    ├── memory_config.json             # Memory ID
    ├── cognito_config.json            # Cognito credentials
    ├── gateway_role_config.json       # IAM role ARN
    ├── lambda_config.json             # Lambda ARN and schema
    └── gateway_config.json            # Gateway URL and ID
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

**Test Date**: 2026-02-20  
**Status**: ✅ ALL CAPABILITIES VERIFIED

| Capability | Status | Evidence |
|------------|--------|----------|
| Memory Integration | ✅ PASS | Recalled email preference |
| Gateway Integration | ✅ PASS | Retrieved order ORD-001 |
| Lambda Invocation | ✅ PASS | Got order details |
| Custom Tools | ✅ PASS | Calculated eligibility |
| OAuth Authentication | ✅ PASS | JWT token obtained |
| Personalization | ✅ PASS | Combined all data |

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
- Integrating AgentCore Memory for personalization
- Using Gateway for external tool access
- Lambda function integration via MCP
- Knowledge Base integration for RAG
- OAuth2 authentication flows
- Custom tool development

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

**Status**: ✅ Production-Ready  
**Version**: 2.0  
**Last Updated**: 2026-02-20
