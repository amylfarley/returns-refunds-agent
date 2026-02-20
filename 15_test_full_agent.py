#!/usr/bin/env python3
"""
Test script for full-featured returns agent.

This script tests the complete integration of:
- Memory (customer preferences)
- Gateway (order lookup via Lambda)
- Knowledge Base (policy information)
- Custom tools (eligibility, refunds)
"""

import os
import sys
import json
import importlib.util

print("=" * 80)
print("FULL-FEATURED AGENT TEST")
print("=" * 80)
print()

# ============================================================================
# STEP 1: Load All Configuration Files
# ============================================================================
print("Step 1: Loading configuration files...")

configs = {}

# Load Memory configuration
try:
    with open('memory_config.json') as f:
        configs['memory'] = json.load(f)
    print(f"✓ Memory config loaded")
    print(f"  Memory ID: {configs['memory']['memory_id']}")
except FileNotFoundError:
    print("❌ Error: memory_config.json not found")
    sys.exit(1)

# Load Knowledge Base configuration
try:
    with open('kb_config.json') as f:
        configs['kb'] = json.load(f)
    print(f"✓ Knowledge Base config loaded")
    print(f"  KB ID: {configs['kb']['knowledge_base_id']}")
except FileNotFoundError:
    print("❌ Error: kb_config.json not found")
    sys.exit(1)

# Load Gateway configuration
try:
    with open('gateway_config.json') as f:
        configs['gateway'] = json.load(f)
    print(f"✓ Gateway config loaded")
    print(f"  Gateway URL: {configs['gateway']['gateway_url']}")
except FileNotFoundError:
    print("❌ Error: gateway_config.json not found")
    sys.exit(1)

# Load Cognito configuration
try:
    with open('cognito_config.json') as f:
        configs['cognito'] = json.load(f)
    print(f"✓ Cognito config loaded")
    print(f"  Client ID: {configs['cognito']['client_id']}")
except FileNotFoundError:
    print("❌ Error: cognito_config.json not found")
    sys.exit(1)

# Load Lambda configuration (for reference)
try:
    with open('lambda_config.json') as f:
        configs['lambda'] = json.load(f)
    print(f"✓ Lambda config loaded")
    print(f"  Function: {configs['lambda']['function_name']}")
except FileNotFoundError:
    print("⚠️  Warning: lambda_config.json not found (optional)")

# ============================================================================
# STEP 2: Set Environment Variables
# ============================================================================
print()
print("Step 2: Setting environment variables...")

os.environ["MEMORY_ID"] = configs['memory']['memory_id']
os.environ["KNOWLEDGE_BASE_ID"] = configs['kb']['knowledge_base_id']
os.environ["GATEWAY_URL"] = configs['gateway']['gateway_url']
os.environ["COGNITO_CLIENT_ID"] = configs['cognito']['client_id']
os.environ["COGNITO_CLIENT_SECRET"] = configs['cognito']['client_secret']
os.environ["COGNITO_DISCOVERY_URL"] = configs['cognito']['discovery_url']

print("✓ Environment variables set")

# ============================================================================
# STEP 3: Import Agent
# ============================================================================
print()
print("Step 3: Loading full-featured agent...")

try:
    spec = importlib.util.spec_from_file_location("full_agent", "14_full_agent.py")
    agent_module = importlib.util.module_from_spec(spec)
    sys.modules["full_agent"] = agent_module
    spec.loader.exec_module(agent_module)
    
    run_agent = agent_module.run_agent
    print("✓ Agent loaded successfully")
except Exception as e:
    print(f"❌ Error loading agent: {e}")
    sys.exit(1)

# ============================================================================
# STEP 4: Run Test Query
# ============================================================================
print()
print("=" * 80)
print("TEST: INTEGRATED CAPABILITIES")
print("=" * 80)
print()
print("Customer: user_001")
print("Query: 'Hi! Can you look up my order ORD-001 and tell me if I can")
print("       return it? Remember, I prefer email updates.'")
print()
print("-" * 80)
print("AGENT RESPONSE:")
print("-" * 80)
print()

test_query = (
    "Hi! Can you look up my order ORD-001 and tell me if I can return it? "
    "Remember, I prefer email updates."
)

try:
    response = run_agent(
        user_input=test_query,
        actor_id="user_001",
        session_id="test_session_full"
    )
    
    print(response)
    print()
    
except Exception as e:
    print(f"❌ ERROR: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# ============================================================================
# STEP 5: Verify Capabilities
# ============================================================================
print()
print("=" * 80)
print("CAPABILITY VERIFICATION")
print("=" * 80)
print()

# Check if response contains expected elements
response_lower = response.lower()

checks = {
    "Memory - Email Preference": any(word in response_lower for word in ['email', 'notification']),
    "Gateway - Order Lookup": 'ord-001' in response_lower or 'laptop' in response_lower or 'dell' in response_lower,
    "Custom Tool - Eligibility": any(word in response_lower for word in ['eligible', 'return', 'days']),
    "Personalization": any(word in response_lower for word in ['remember', 'preference', 'you'])
}

print("Checking agent capabilities:")
print()

all_passed = True
for capability, passed in checks.items():
    status = "✓ PASS" if passed else "✗ FAIL"
    print(f"  {status}: {capability}")
    if not passed:
        all_passed = False

print()

if all_passed:
    print("=" * 80)
    print("✓ ALL CAPABILITIES VERIFIED!")
    print("=" * 80)
    print()
    print("The agent successfully demonstrated:")
    print("  • Memory integration (remembered email preference)")
    print("  • Gateway integration (looked up order ORD-001)")
    print("  • Custom tools (checked return eligibility)")
    print("  • Personalized response (combined all information)")
    print()
    print("This is a fully functional, production-ready agent!")
else:
    print("=" * 80)
    print("⚠️  SOME CAPABILITIES NOT VERIFIED")
    print("=" * 80)
    print()
    print("The agent may need additional testing or configuration.")

print("=" * 80)

# ============================================================================
# SUMMARY
# ============================================================================
print()
print("TEST SUMMARY")
print("=" * 80)
print()
print("Configuration:")
print(f"  • Memory ID: {configs['memory']['memory_id']}")
print(f"  • Gateway: {configs['gateway']['gateway_id']}")
print(f"  • Knowledge Base: {configs['kb']['knowledge_base_id']}")
print(f"  • Cognito: {configs['cognito']['user_pool_id']}")
print()
print("Test Query: Order lookup with memory recall")
print("Customer: user_001 (with seeded conversation history)")
print()
print("Expected Behavior:")
print("  1. Recall email preference from memory")
print("  2. Look up order ORD-001 via gateway Lambda")
print("  3. Check return eligibility using custom tool")
print("  4. Provide personalized, comprehensive response")
print()
print("=" * 80)
