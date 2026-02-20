#!/usr/bin/env python3
"""
Script to create Lambda function for order lookup.

This script creates:
- Lambda function that looks up order details by order ID
- IAM role for Lambda execution
- Mock data with sample orders
- Tool schema for gateway integration
"""

import boto3
import json
import time
import zipfile
import io
from datetime import datetime, timedelta

# Configuration
REGION = 'us-west-2'
FUNCTION_NAME = 'OrderLookupFunction'
ROLE_NAME = 'OrderLookupLambdaRole'

print("=" * 80)
print("LAMBDA FUNCTION SETUP FOR ORDER LOOKUP")
print("=" * 80)
print()

# Create clients
iam_client = boto3.client('iam')
lambda_client = boto3.client('lambda', region_name=REGION)
sts_client = boto3.client('sts', region_name=REGION)

# Get AWS account ID
try:
    account_id = sts_client.get_caller_identity()['Account']
    print(f"AWS Account ID: {account_id}")
    print()
except Exception as e:
    print(f"❌ Error getting account ID: {e}")
    exit(1)

# ============================================================================
# STEP 1: Create Lambda Execution Role
# ============================================================================
print("Step 1: Creating Lambda execution role...")

# Trust policy for Lambda
lambda_trust_policy = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {
                "Service": "lambda.amazonaws.com"
            },
            "Action": "sts:AssumeRole"
        }
    ]
}

try:
    # Check if role already exists
    try:
        role_response = iam_client.get_role(RoleName=ROLE_NAME)
        lambda_role_arn = role_response['Role']['Arn']
        print(f"✓ Using existing role: {lambda_role_arn}")
    except iam_client.exceptions.NoSuchEntityException:
        # Create new role
        role_response = iam_client.create_role(
            RoleName=ROLE_NAME,
            AssumeRolePolicyDocument=json.dumps(lambda_trust_policy),
            Description='Execution role for OrderLookupFunction Lambda'
        )
        lambda_role_arn = role_response['Role']['Arn']
        print(f"✓ Role created: {lambda_role_arn}")
        
        # Attach basic Lambda execution policy
        iam_client.attach_role_policy(
            RoleName=ROLE_NAME,
            PolicyArn='arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole'
        )
        print(f"✓ Attached AWSLambdaBasicExecutionRole policy")
        
        # Wait for role to propagate
        print("  Waiting 10 seconds for IAM propagation...")
        time.sleep(10)
        
except Exception as e:
    print(f"❌ Error creating Lambda role: {e}")
    exit(1)

# ============================================================================
# STEP 2: Create Lambda Function Code
# ============================================================================
print()
print("Step 2: Creating Lambda function code...")

# Calculate dates for mock data
today = datetime.now()
recent_date = (today - timedelta(days=15)).strftime('%Y-%m-%d')
old_date = (today - timedelta(days=45)).strftime('%Y-%m-%d')
defective_date = (today - timedelta(days=10)).strftime('%Y-%m-%d')

lambda_code = f'''
import json
from datetime import datetime, timedelta

# Mock order database
ORDERS = {{
    "ORD-001": {{
        "order_id": "ORD-001",
        "product_name": "Dell XPS 15 Laptop",
        "purchase_date": "{recent_date}",
        "amount": 1299.99,
        "category": "electronics",
        "status": "delivered"
    }},
    "ORD-002": {{
        "order_id": "ORD-002",
        "product_name": "iPhone 13",
        "purchase_date": "{old_date}",
        "amount": 799.99,
        "category": "electronics",
        "status": "delivered"
    }},
    "ORD-003": {{
        "order_id": "ORD-003",
        "product_name": "Samsung Galaxy Tab (Defective)",
        "purchase_date": "{defective_date}",
        "amount": 449.99,
        "category": "electronics",
        "status": "delivered"
    }}
}}

def check_return_eligibility(purchase_date, category):
    """Check if order is eligible for return"""
    try:
        purchase_dt = datetime.strptime(purchase_date, '%Y-%m-%d')
        days_since_purchase = (datetime.now() - purchase_dt).days
        
        # 30-day return window for electronics
        return_window = 30
        
        if days_since_purchase <= return_window:
            return {{
                "eligible": True,
                "reason": f"Within {{return_window}}-day return window",
                "days_remaining": return_window - days_since_purchase
            }}
        else:
            return {{
                "eligible": False,
                "reason": f"Exceeded {{return_window}}-day return window",
                "days_remaining": 0
            }}
    except Exception as e:
        return {{
            "eligible": False,
            "reason": f"Error checking eligibility: {{str(e)}}",
            "days_remaining": 0
        }}

def lambda_handler(event, context):
    """
    Lambda handler for order lookup.
    
    Expected input:
    {{
        "order_id": "ORD-001"
    }}
    """
    try:
        # Parse input
        if isinstance(event, str):
            event = json.loads(event)
        
        order_id = event.get('order_id', '').upper()
        
        if not order_id:
            return {{
                'statusCode': 400,
                'body': json.dumps({{
                    'error': 'order_id is required'
                }})
            }}
        
        # Look up order
        order = ORDERS.get(order_id)
        
        if not order:
            return {{
                'statusCode': 404,
                'body': json.dumps({{
                    'error': f'Order {{order_id}} not found',
                    'available_orders': list(ORDERS.keys())
                }})
            }}
        
        # Check return eligibility
        eligibility = check_return_eligibility(
            order['purchase_date'],
            order['category']
        )
        
        # Build response
        response_data = {{
            **order,
            'return_eligibility': eligibility
        }}
        
        return {{
            'statusCode': 200,
            'body': json.dumps(response_data)
        }}
        
    except Exception as e:
        return {{
            'statusCode': 500,
            'body': json.dumps({{
                'error': f'Internal error: {{str(e)}}'
            }})
        }}
'''

print("✓ Lambda code created with mock order data")
print(f"  Sample orders: ORD-001 (recent laptop), ORD-002 (old phone), ORD-003 (defective tablet)")

# ============================================================================
# STEP 3: Package Lambda Code
# ============================================================================
print()
print("Step 3: Packaging Lambda code...")

# Create ZIP file in memory
zip_buffer = io.BytesIO()
with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
    zip_file.writestr('lambda_function.py', lambda_code)

zip_buffer.seek(0)
lambda_zip = zip_buffer.read()

print(f"✓ Lambda code packaged (size: {len(lambda_zip)} bytes)")

# ============================================================================
# STEP 4: Create or Update Lambda Function
# ============================================================================
print()
print("Step 4: Creating Lambda function...")
print(f"  Function Name: {FUNCTION_NAME}")

try:
    # Check if function already exists
    try:
        lambda_client.get_function(FunctionName=FUNCTION_NAME)
        # Function exists, update it
        print("  Function already exists, updating code...")
        update_response = lambda_client.update_function_code(
            FunctionName=FUNCTION_NAME,
            ZipFile=lambda_zip
        )
        function_arn = update_response['FunctionArn']
        print(f"✓ Function updated: {function_arn}")
    except lambda_client.exceptions.ResourceNotFoundException:
        # Create new function
        create_response = lambda_client.create_function(
            FunctionName=FUNCTION_NAME,
            Runtime='python3.12',
            Role=lambda_role_arn,
            Handler='lambda_function.lambda_handler',
            Code={'ZipFile': lambda_zip},
            Description='Order lookup function for returns agent',
            Timeout=30,
            MemorySize=128
        )
        function_arn = create_response['FunctionArn']
        print(f"✓ Function created: {function_arn}")
        
        # Wait for function to be active
        print("  Waiting for function to be active...")
        time.sleep(5)
        
except Exception as e:
    print(f"❌ Error creating Lambda function: {e}")
    exit(1)

# ============================================================================
# STEP 5: Create Tool Schema
# ============================================================================
print()
print("Step 5: Creating tool schema for gateway integration...")

tool_schema = {
    "inlinePayload": [
        {
            "name": "lookup_order",
            "description": "Look up order details by order ID. Returns order information including product name, purchase date, amount, and return eligibility status.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "order_id": {
                        "type": "string",
                        "description": "The order ID to look up (e.g., ORD-001, ORD-002, ORD-003)"
                    }
                },
                "required": ["order_id"]
            }
        }
    ]
}

print("✓ Tool schema created")
print("  Tool name: lookup_order")
print("  Input: order_id (string)")

# ============================================================================
# STEP 6: Save Configuration
# ============================================================================
print()
print("Step 6: Saving configuration to lambda_config.json...")

config = {
    "function_name": FUNCTION_NAME,
    "function_arn": function_arn,
    "tool_schema": tool_schema,
    "tool_name": "lookup_order",
    "region": REGION,
    "sample_orders": ["ORD-001", "ORD-002", "ORD-003"]
}

try:
    with open('lambda_config.json', 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"✓ Configuration saved to lambda_config.json")
    
except Exception as e:
    print(f"❌ Error saving configuration: {e}")
    exit(1)

# ============================================================================
# SUMMARY
# ============================================================================
print()
print("=" * 80)
print("LAMBDA FUNCTION SETUP COMPLETE")
print("=" * 80)
print()
print(f"Function ARN: {function_arn}")
print(f"Function Name: {FUNCTION_NAME}")
print(f"Tool Name: lookup_order")
print()
print("Sample Orders:")
print(f"  ORD-001: Dell XPS 15 Laptop (purchased {recent_date}, eligible for return)")
print(f"  ORD-002: iPhone 13 (purchased {old_date}, NOT eligible - too old)")
print(f"  ORD-003: Samsung Galaxy Tab (purchased {defective_date}, eligible for return)")
print()
print("Configuration saved to: lambda_config.json")
print()
print("This Lambda function:")
print("  ✓ Looks up order details by order ID")
print("  ✓ Checks return eligibility (30-day window)")
print("  ✓ Returns product info and eligibility status")
print("  ✓ Ready to be added as a gateway target")
print("=" * 80)
