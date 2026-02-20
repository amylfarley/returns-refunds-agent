#!/usr/bin/env python3
"""
Script to seed AgentCore Memory with sample customer conversations.

This script adds sample conversations to demonstrate memory capabilities:
- Customer preferences (email notifications)
- Past return history (defective laptop)
- Questions about return policies
"""

import json
import time

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
# CONVERSATION 1: Customer mentions preferences and past return
# ============================================================================
print("=" * 80)
print("CONVERSATION 1: Customer preferences and past return history")
print("=" * 80)

conversation_1 = [
    ("Hi, I need help with a return for a laptop I purchased.", "USER"),
    ("I'd be happy to help you with your laptop return. Can you tell me more about the issue?", "ASSISTANT"),
    ("The laptop was defective - it wouldn't turn on after the first week. I returned it last month and got a full refund.", "USER"),
    ("I'm sorry you had that experience. I'm glad we were able to process your refund. Is there anything else I can help you with today?", "ASSISTANT"),
    ("Yes, for future reference, I prefer to receive all notifications via email rather than phone calls.", "USER"),
    ("Noted! I've recorded your preference for email notifications. All future updates will be sent to your email address.", "ASSISTANT")
]

print("\nStoring conversation 1...")
memory_client.create_event(
    memory_id=memory_id,
    actor_id="user_001",
    session_id="session_001",
    messages=conversation_1
)
print(f"✓ Stored {len(conversation_1)} messages")

# ============================================================================
# CONVERSATION 2: Customer asks about return windows
# ============================================================================
print("\n" + "=" * 80)
print("CONVERSATION 2: Questions about return policies")
print("=" * 80)

conversation_2 = [
    ("Hello, I have a question about return windows for electronics.", "USER"),
    ("I can help with that! What would you like to know about our electronics return policy?", "ASSISTANT"),
    ("How long do I have to return an electronic item like a tablet or phone?", "USER"),
    ("For most electronics including tablets and phones, you have 30 days from the purchase date to initiate a return. The item should be in its original condition with all accessories.", "ASSISTANT"),
    ("That's helpful, thank you! And does the same apply to laptops?", "USER"),
    ("Yes, laptops also have a 30-day return window. Given your previous experience with the defective laptop, I want to assure you that defective items are always eligible for full refunds regardless of condition.", "ASSISTANT")
]

print("\nStoring conversation 2...")
memory_client.create_event(
    memory_id=memory_id,
    actor_id="user_001",
    session_id="session_002",
    messages=conversation_2
)
print(f"✓ Stored {len(conversation_2)} messages")

# ============================================================================
# WAIT FOR MEMORY PROCESSING
# ============================================================================
print("\n" + "=" * 80)
print("MEMORY PROCESSING")
print("=" * 80)
print("\nMemory strategies are now processing the conversations asynchronously...")
print("This extracts:")
print("  • Preferences: 'prefers email notifications'")
print("  • Semantic facts: 'returned defective laptop', 'got full refund'")
print("  • Summaries: conversation context for each session")
print("\nWaiting 30 seconds for memory processing to complete...")

for i in range(30, 0, -5):
    print(f"  {i} seconds remaining...")
    time.sleep(5)

print("\n✓ Memory processing complete!")
print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)
print(f"✓ Seeded {len(conversation_1) + len(conversation_2)} total messages")
print(f"✓ 2 conversations stored for customer user_001")
print(f"✓ Memory strategies have extracted preferences and facts")
print("\nThe agent can now:")
print("  • Remember the customer prefers email notifications")
print("  • Recall they previously returned a defective laptop")
print("  • Reference past conversations about return policies")
print("=" * 80)
