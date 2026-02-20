#!/usr/bin/env python3
"""
Test script for memory-enabled returns agent.

This script tests if the agent can recall customer preferences and history
from AgentCore Memory.
"""

import os
import sys
import json
import importlib.util

# Load configuration files
print("Loading configuration...")
print("=" * 80)

# Load Memory ID from memory_config.json
try:
    with open('memory_config.json') as f:
        memory_config = json.load(f)
        memory_id = memory_config['memory_id']
        print(f"✓ Memory ID loaded: {memory_id}")
except FileNotFoundError:
    print("❌ Error: memory_config.json not found")
    print("   Run 03_create_memory.py first to create memory")
    sys.exit(1)

# Load Knowledge Base ID from kb_config.json
try:
    with open('kb_config.json') as f:
        kb_config = json.load(f)
        kb_id = kb_config['knowledge_base_id']
        print(f"✓ Knowledge Base ID loaded: {kb_id}")
except FileNotFoundError:
    print("❌ Error: kb_config.json not found")
    sys.exit(1)

# Set environment variables (the agent will also load from files, but this ensures compatibility)
os.environ["MEMORY_ID"] = memory_id
os.environ["KNOWLEDGE_BASE_ID"] = kb_id

print("=" * 80)
print()

# Import run_agent from 06_memory_enabled_agent.py using importlib
print("Loading memory-enabled agent...")
spec = importlib.util.spec_from_file_location("memory_agent", "06_memory_enabled_agent.py")
agent_module = importlib.util.module_from_spec(spec)
sys.modules["memory_agent"] = agent_module
spec.loader.exec_module(agent_module)

run_agent = agent_module.run_agent
print("✓ Agent loaded successfully")
print()

# ============================================================================
# TEST: Ask agent what it remembers about user_001
# ============================================================================
print("=" * 80)
print("MEMORY RECALL TEST")
print("=" * 80)
print()
print("Customer: user_001")
print("Question: 'Hi! I'm thinking about returning something. What do you remember about my preferences?'")
print()
print("-" * 80)
print("AGENT RESPONSE:")
print("-" * 80)
print()

try:
    # Run agent with user_001 as the actor_id to retrieve their memories
    response = run_agent(
        user_input="Hi! I'm thinking about returning something. What do you remember about my preferences?",
        actor_id="user_001",
        session_id="test_session_001"
    )
    
    print(response)
    print()
    
except Exception as e:
    print(f"❌ ERROR: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# ============================================================================
# ANALYSIS
# ============================================================================
print()
print("=" * 80)
print("EXPECTED MEMORY RECALL")
print("=" * 80)
print()
print("The agent should remember:")
print("  ✓ Customer prefers email notifications (not phone calls)")
print("  ✓ Previously returned a defective laptop")
print("  ✓ Received a full refund for the laptop")
print("  ✓ Asked about return windows for electronics")
print()
print("If the agent mentions these details, memory integration is working!")
print("=" * 80)
