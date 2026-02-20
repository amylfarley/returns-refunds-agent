#!/usr/bin/env python3
"""
Script to test AgentCore Memory retrieval.

This script retrieves memories for user_001 from all three namespaces:
- Preferences: Customer communication preferences
- Semantic: Facts about returns and past interactions
- Summary: Conversation summaries
"""

import json

try:
    from bedrock_agentcore.memory import MemoryClient
except ImportError:
    print("✗ Error: bedrock_agentcore package not found")
    print("  Install with: pip install bedrock-agentcore")
    exit(1)

# Load memory_id from config
print("Loading memory configuration...")
with open('memory_config.json') as f:
    config = json.load(f)
    memory_id = config['memory_id']

print(f"✓ Using Memory ID: {memory_id}")
print(f"✓ Region: us-west-2")
print(f"✓ Customer ID: user_001\n")

# Create memory client
memory_client = MemoryClient(region_name='us-west-2')

# ============================================================================
# TEST 1: Retrieve from PREFERENCES namespace
# ============================================================================
print("=" * 80)
print("TEST 1: PREFERENCES NAMESPACE")
print("=" * 80)
print("Namespace: app/user_001/preferences")
print("Query: 'customer preferences and communication'\n")

try:
    preferences = memory_client.retrieve_memories(
        memory_id=memory_id,
        namespace="app/user_001/preferences",
        query="customer preferences and communication",
        top_k=5
    )
    
    if preferences:
        print(f"✓ Retrieved {len(preferences)} preference memories\n")
        
        for i, memory in enumerate(preferences, 1):
            print(f"Preference {i}:")
            print("─" * 80)
            content = memory.get('content', {})
            if isinstance(content, dict):
                text = content.get('text', 'N/A')
            else:
                text = str(content)
            print(f"Content: {text}")
            
            relevance = memory.get('relevanceScore', 'N/A')
            if isinstance(relevance, (int, float)):
                print(f"Relevance Score: {relevance:.3f}")
            else:
                print(f"Relevance Score: {relevance}")
            print()
    else:
        print("⚠️  No preference memories found")
        print("Memory extraction may still be processing (takes 20-30 seconds)\n")
        
except Exception as e:
    print(f"❌ Error retrieving preferences: {e}\n")

# ============================================================================
# TEST 2: Retrieve from SEMANTIC namespace
# ============================================================================
print("=" * 80)
print("TEST 2: SEMANTIC NAMESPACE")
print("=" * 80)
print("Namespace: app/user_001/semantic")
print("Query: 'return history and past purchases'\n")

try:
    semantic = memory_client.retrieve_memories(
        memory_id=memory_id,
        namespace="app/user_001/semantic",
        query="return history and past purchases",
        top_k=5
    )
    
    if semantic:
        print(f"✓ Retrieved {len(semantic)} semantic memories\n")
        
        for i, memory in enumerate(semantic, 1):
            print(f"Fact {i}:")
            print("─" * 80)
            content = memory.get('content', {})
            if isinstance(content, dict):
                text = content.get('text', 'N/A')
            else:
                text = str(content)
            print(f"Content: {text}")
            
            relevance = memory.get('relevanceScore', 'N/A')
            if isinstance(relevance, (int, float)):
                print(f"Relevance Score: {relevance:.3f}")
            else:
                print(f"Relevance Score: {relevance}")
            print()
    else:
        print("⚠️  No semantic memories found")
        print("Memory extraction may still be processing (takes 20-30 seconds)\n")
        
except Exception as e:
    print(f"❌ Error retrieving semantic memories: {e}\n")

# ============================================================================
# TEST 3: Retrieve from SUMMARY namespace (session 001)
# ============================================================================
print("=" * 80)
print("TEST 3: SUMMARY NAMESPACE (Session 001)")
print("=" * 80)
print("Namespace: app/user_001/session_001/summary")
print("Query: 'conversation summary'\n")

try:
    summary = memory_client.retrieve_memories(
        memory_id=memory_id,
        namespace="app/user_001/session_001/summary",
        query="conversation summary",
        top_k=3
    )
    
    if summary:
        print(f"✓ Retrieved {len(summary)} summary memories\n")
        
        for i, memory in enumerate(summary, 1):
            print(f"Summary {i}:")
            print("─" * 80)
            content = memory.get('content', {})
            if isinstance(content, dict):
                text = content.get('text', 'N/A')
            else:
                text = str(content)
            print(f"Content: {text}")
            
            relevance = memory.get('relevanceScore', 'N/A')
            if isinstance(relevance, (int, float)):
                print(f"Relevance Score: {relevance:.3f}")
            else:
                print(f"Relevance Score: {relevance}")
            print()
    else:
        print("⚠️  No summary memories found")
        print("Memory extraction may still be processing (takes 20-30 seconds)\n")
        
except Exception as e:
    print(f"❌ Error retrieving summaries: {e}\n")

# ============================================================================
# SUMMARY
# ============================================================================
print("=" * 80)
print("WHAT THE AGENT REMEMBERS ABOUT user_001")
print("=" * 80)
print("\nThe agent has access to:")
print("  • Customer preferences (email notifications)")
print("  • Past return history (defective laptop)")
print("  • Previous conversations about return policies")
print("\nThis allows the agent to provide personalized, context-aware responses!")
print("=" * 80)
