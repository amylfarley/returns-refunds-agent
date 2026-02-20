"""
AgentCore Runtime Agent: returns_agent_runtime
Production-ready agent with Memory, Gateway, and Knowledge Base integration

This agent is ready to deploy to AgentCore Runtime with:
1. BedrockAgentCoreApp entrypoint
2. Memory integration for customer preferences
3. Gateway tools for order lookup
4. Knowledge Base access for policy retrieval
5. Custom tools for return processing
6. Comprehensive error handling
"""

import os
import json
import traceback
from datetime import datetime
from bedrock_agentcore.runtime import BedrockAgentCoreApp
from strands import Agent, tool
from strands.models import BedrockModel
from strands_tools import retrieve, current_time
from strands.tools.mcp import MCPClient
from mcp.client.streamable_http import streamablehttp_client
import requests
from bedrock_agentcore.memory.integrations.strands.config import AgentCoreMemoryConfig, RetrievalConfig
from bedrock_agentcore.memory.integrations.strands.session_manager import AgentCoreMemorySessionManager

# Constants
MODEL_ID = "us.anthropic.claude-sonnet-4-5-20250929-v1:0"
REGION = "us-west-2"
SESSION_ID = "default-session"
ACTOR_ID = "default-actor"

# Initialize app
app = BedrockAgentCoreApp()

# ============================================================================
# CUSTOM TOOLS (from original agent)
# ============================================================================

@tool
def check_return_eligibility(purchase_date: str, category: str) -> dict:
    """
    Check if an item is eligible for return based on purchase date and category.
    
    Args:
        purchase_date: Purchase date in YYYY-MM-DD format
        category: Product category (e.g., 'electronics', 'clothing', 'books')
    
    Returns:
        Dictionary with eligibility status and reason
    """
    try:
        purchase_dt = datetime.strptime(purchase_date, '%Y-%m-%d')
        days_since_purchase = (datetime.now() - purchase_dt).days
        
        # Return windows by category
        return_windows = {
            'electronics': 30,
            'clothing': 30,
            'books': 30,
            'grocery': 30,
            'jewelry': 30,
            'default': 30
        }
        
        window = return_windows.get(category.lower(), return_windows['default'])
        
        if days_since_purchase < 0:
            return {
                'eligible': False,
                'reason': 'Purchase date is in the future',
                'days_remaining': 0
            }
        elif days_since_purchase <= window:
            return {
                'eligible': True,
                'reason': f'Within {window}-day return window',
                'days_remaining': window - days_since_purchase
            }
        else:
            return {
                'eligible': False,
                'reason': f'Exceeded {window}-day return window',
                'days_remaining': 0
            }
    except ValueError:
        return {
            'eligible': False,
            'reason': 'Invalid date format. Use YYYY-MM-DD',
            'days_remaining': 0
        }
    except Exception as e:
        print(f"Error in check_return_eligibility: {e}")
        return {
            'eligible': False,
            'reason': f'Error checking eligibility: {str(e)}',
            'days_remaining': 0
        }

@tool
def calculate_refund_amount(original_price: float, condition: str, return_reason: str) -> dict:
    """
    Calculate refund amount based on price, condition, and return reason.
    
    Args:
        original_price: Original purchase price
        condition: Item condition ('new', 'opened', 'used', 'damaged')
        return_reason: Reason for return ('defective', 'wrong_item', 'changed_mind', 'not_as_described')
    
    Returns:
        Dictionary with refund amount and breakdown
    """
    try:
        if original_price < 0:
            return {
                'refund_amount': 0.0,
                'deduction': 0.0,
                'reason': 'Invalid price'
            }
        
        # Condition-based deductions
        condition_deductions = {
            'new': 0.0,
            'opened': 0.0,
            'used': 0.20,  # 20% deduction
            'damaged': 0.50  # 50% deduction
        }
        
        # Reason-based adjustments (defective/wrong items get full refund)
        full_refund_reasons = ['defective', 'wrong_item', 'not_as_described']
        
        if return_reason.lower() in full_refund_reasons:
            # Full refund regardless of condition for seller errors
            refund_amount = original_price
            deduction = 0.0
            reason = 'Full refund - seller error'
        else:
            # Apply condition-based deduction
            deduction_rate = condition_deductions.get(condition.lower(), 0.20)
            deduction = original_price * deduction_rate
            refund_amount = original_price - deduction
            reason = f'{int(deduction_rate * 100)}% deduction for {condition} condition'
        
        return {
            'refund_amount': round(refund_amount, 2),
            'deduction': round(deduction, 2),
            'original_price': original_price,
            'reason': reason
        }
    except Exception as e:
        print(f"Error in calculate_refund_amount: {e}")
        return {
            'refund_amount': 0.0,
            'deduction': 0.0,
            'reason': f'Error calculating refund: {str(e)}'
        }

@tool
def format_policy_response(policy_text: str, customer_question: str = '') -> str:
    """
    Format policy information in a customer-friendly way.
    
    Args:
        policy_text: Raw policy text from knowledge base
        customer_question: Optional customer question for context
    
    Returns:
        Formatted, customer-friendly policy response
    """
    try:
        # Add friendly header
        formatted = '📋 Return Policy Information\n'
        formatted += '=' * 50 + '\n\n'
        
        if customer_question:
            formatted += f'Regarding: {customer_question}\n\n'
        
        # Clean up and format the policy text
        lines = policy_text.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                formatted += '\n'
            elif line.isupper() or line.endswith(':'):
                # Treat as section header
                formatted += f'\n{line}\n'
            elif line.startswith('-') or line.startswith('•'):
                # Keep bullet points
                formatted += f'  {line}\n'
            else:
                # Regular text
                formatted += f'{line}\n'
        
        formatted += '\n' + '=' * 50 + '\n'
        formatted += '💡 Tip: If you have specific questions about your return, I can help!\n'
        
        return formatted
    except Exception as e:
        print(f"Error in format_policy_response: {e}")
        return f"Error formatting policy: {str(e)}"

# ============================================================================
# GATEWAY HELPER FUNCTIONS
# ============================================================================

def get_cognito_token_with_scope(client_id, client_secret, discovery_url, scope):
    """Get Cognito bearer token with a specific OAuth scope"""
    try:
        # Extract token endpoint from discovery URL
        discovery_response = requests.get(discovery_url, timeout=10)
        discovery_response.raise_for_status()
        token_endpoint = discovery_response.json()['token_endpoint']
        
        # Get token using client credentials flow
        response = requests.post(
            token_endpoint,
            data={
                'grant_type': 'client_credentials',
                'client_id': client_id,
                'client_secret': client_secret,
                'scope': scope
            },
            headers={'Content-Type': 'application/x-www-form-urlencoded'},
            timeout=10
        )
        
        response.raise_for_status()
        return response.json()["access_token"]
    except Exception as e:
        print(f"Error getting Cognito token: {e}")
        raise

def create_mcp_client():
    """Create MCP client for gateway access"""
    try:
        # Get environment variables
        gateway_url = os.environ.get("GATEWAY_URL")
        cognito_client_id = os.environ.get("COGNITO_CLIENT_ID")
        cognito_client_secret = os.environ.get("COGNITO_CLIENT_SECRET")
        cognito_discovery_url = os.environ.get("COGNITO_DISCOVERY_URL")
        oauth_scopes = os.environ.get("OAUTH_SCOPES", "gateway-api/read gateway-api/write")
        
        if not all([gateway_url, cognito_client_id, cognito_client_secret, cognito_discovery_url]):
            print("Warning: Gateway environment variables not set - gateway tools will not be available")
            return None
        
        token = get_cognito_token_with_scope(
            cognito_client_id,
            cognito_client_secret,
            cognito_discovery_url,
            oauth_scopes
        )
        
        print(f"✓ Gateway configured: {gateway_url}")
        return MCPClient(
            lambda: streamablehttp_client(
                gateway_url,
                headers={"Authorization": f"Bearer {token}"},
            )
        )
    except Exception as e:
        print(f"Warning: Failed to create MCP client: {e}")
        return None

# ============================================================================
# RUNTIME ENTRYPOINT
# ============================================================================

@app.entrypoint
def invoke(payload, context=None):
    """AgentCore Runtime entrypoint with comprehensive error handling"""
    try:
        print("=" * 80)
        print("AGENT INVOCATION STARTED")
        print("=" * 80)
        
        # Initialize model
        bedrock_model = BedrockModel(model_id=MODEL_ID, temperature=0.3)
        print(f"✓ Model initialized: {MODEL_ID}")
        
        # Load configuration from environment variables
        memory_id = os.environ.get("MEMORY_ID")
        kb_id = os.environ.get("KNOWLEDGE_BASE_ID")
        
        if not memory_id:
            error_msg = "Error: MEMORY_ID environment variable is required"
            print(f"✗ {error_msg}")
            return error_msg
        
        if not kb_id:
            error_msg = "Error: KNOWLEDGE_BASE_ID environment variable is required"
            print(f"✗ {error_msg}")
            return error_msg
        
        print(f"✓ Memory ID: {memory_id}")
        print(f"✓ Knowledge Base ID: {kb_id}")
        
        # Get session and actor IDs
        session_id = context.session_id if context else SESSION_ID
        actor_id = payload.get("actor_id", ACTOR_ID)
        print(f"✓ Session ID: {session_id}")
        print(f"✓ Actor ID: {actor_id}")
        
        # Configure memory with retrieval settings
        agentcore_memory_config = AgentCoreMemoryConfig(
            memory_id=memory_id,
            session_id=session_id,
            actor_id=actor_id,
            retrieval_config={
                f"app/{actor_id}/semantic": RetrievalConfig(top_k=3),
                f"app/{actor_id}/preferences": RetrievalConfig(top_k=3),
                f"app/{actor_id}/{session_id}/summary": RetrievalConfig(top_k=2),
            }
        )
        
        session_manager = AgentCoreMemorySessionManager(
            agentcore_memory_config=agentcore_memory_config,
            region_name=REGION
        )
        print("✓ Memory session manager configured")
        
        # System prompt with KB ID
        system_prompt = f"""Production returns assistant with full memory and gateway capabilities. Use the retrieve tool to access Amazon return policy documents for accurate information.

When using the retrieve tool, always pass these parameters:
- knowledgeBaseId: {kb_id}
- region: {REGION}
- text: the search query

You have access to:
- Gateway tools for external operations (order lookup)
- Customer conversation history and preferences through memory
- Custom tools for return eligibility and refund calculations"""
        
        # Build custom tools list
        custom_tools = [retrieve, current_time, check_return_eligibility, calculate_refund_amount, format_policy_response]
        print(f"✓ Custom tools loaded: {len(custom_tools)} tools")
        
        # Try to create MCP client for gateway tools
        mcp_client = create_mcp_client()
        
        if mcp_client:
            try:
                # Keep MCP client active during agent execution
                with mcp_client:
                    # Get gateway tools from MCP client
                    gateway_tools = list(mcp_client.list_tools_sync())
                    print(f"✓ Gateway tools loaded: {len(gateway_tools)} tools")
                    
                    # Create agent with all tools
                    agent = Agent(
                        model=bedrock_model,
                        tools=custom_tools + gateway_tools,
                        system_prompt=system_prompt,
                        session_manager=session_manager
                    )
                    
                    user_input = payload.get("prompt", "")
                    print(f"✓ Processing query: {user_input[:100]}...")
                    
                    response = agent(user_input)
                    result = response.message["content"][0]["text"]
                    
                    print("✓ Agent response generated successfully")
                    print("=" * 80)
                    return result
            except Exception as e:
                print(f"⚠️  Failed to use gateway tools: {e}")
                print("Falling back to agent without gateway tools")
                traceback.print_exc()
        
        # Create agent without gateway tools (fallback)
        print("✓ Creating agent without gateway tools")
        agent = Agent(
            model=bedrock_model,
            tools=custom_tools,
            system_prompt=system_prompt,
            session_manager=session_manager
        )
        
        user_input = payload.get("prompt", "")
        print(f"✓ Processing query: {user_input[:100]}...")
        
        response = agent(user_input)
        result = response.message["content"][0]["text"]
        
        print("✓ Agent response generated successfully")
        print("=" * 80)
        return result
    
    except Exception as e:
        error_msg = f"Agent invocation failed: {str(e)}"
        print(f"✗ {error_msg}")
        traceback.print_exc()
        print("=" * 80)
        return error_msg

if __name__ == "__main__":
    app.run()
