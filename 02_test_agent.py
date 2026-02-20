"""
Test script for returns_refunds_agent
Tests various customer service scenarios
"""

import os
import sys
import importlib.util
from datetime import datetime, timedelta

# Set required environment variables
os.environ["KNOWLEDGE_BASE_ID"] = "XWCNYZDEGT"

# Import run_agent from 01_returns_refunds_agent.py using importlib
spec = importlib.util.spec_from_file_location("returns_refunds_agent", "01_returns_refunds_agent.py")
agent_module = importlib.util.module_from_spec(spec)
sys.modules["returns_refunds_agent"] = agent_module
spec.loader.exec_module(agent_module)

run_agent = agent_module.run_agent

# Test questions
test_questions = [
    {
        "name": "Test 1: Current Time",
        "question": "What time is it?"
    },
    {
        "name": "Test 2: Return Eligibility",
        "question": f"Can I return a laptop I purchased 25 days ago? The purchase date was {(datetime.now() - timedelta(days=25)).strftime('%Y-%m-%d')}."
    },
    {
        "name": "Test 3: Refund Calculation",
        "question": "Calculate my refund for a $500 item returned due to defect in like-new condition. The original price is $500, condition is 'new', and return reason is 'defective'."
    },
    {
        "name": "Test 4: Return Policy Explanation",
        "question": "Explain the return policy for electronics in a simple way. Please use the retrieve tool to search the knowledge base for 'Amazon return policy for electronics' and format the response in a customer-friendly manner."
    },
    {
        "name": "Test 5: Knowledge Base Retrieval",
        "question": "Use the retrieve tool to search the knowledge base for 'Amazon return policy for electronics' and tell me what you find."
    }
]

def run_tests():
    """Run all test questions against the agent"""
    print("=" * 80)
    print("RETURNS & REFUNDS AGENT - TEST SUITE")
    print("=" * 80)
    print(f"\nKnowledge Base ID: {os.environ.get('KNOWLEDGE_BASE_ID')}")
    print(f"Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\n" + "=" * 80 + "\n")
    
    for i, test in enumerate(test_questions, 1):
        print(f"\n{'=' * 80}")
        print(f"{test['name']}")
        print(f"{'=' * 80}")
        print(f"\nQuestion: {test['question']}\n")
        print("-" * 80)
        print("Agent Response:")
        print("-" * 80)
        
        try:
            response = run_agent(test['question'])
            print(response)
        except Exception as e:
            print(f"❌ ERROR: {str(e)}")
            import traceback
            traceback.print_exc()
        
        print("\n" + "=" * 80)
        
        # Pause between tests to avoid rate limiting
        if i < len(test_questions):
            print("\nWaiting 2 seconds before next test...\n")
            import time
            time.sleep(2)
    
    print("\n" + "=" * 80)
    print("TEST SUITE COMPLETED")
    print("=" * 80)

if __name__ == "__main__":
    run_tests()
