#!/usr/bin/env python3
"""
Script to create Cognito User Pool for Gateway authentication.

This script sets up:
- Cognito User Pool (secure login system)
- Domain prefix for OAuth endpoints
- App client with client credentials for machine-to-machine auth
- OAuth2 configuration with read/write permissions
"""

import boto3
import json
import time
import uuid

# Configuration
REGION = 'us-west-2'
POOL_NAME = f'returns-gateway-pool-{uuid.uuid4().hex[:8]}'
DOMAIN_PREFIX = f'returns-gateway-{uuid.uuid4().hex[:8]}'
APP_CLIENT_NAME = 'returns-gateway-client'

print("=" * 80)
print("COGNITO USER POOL SETUP FOR GATEWAY AUTHENTICATION")
print("=" * 80)
print()

# Create Cognito client
cognito_client = boto3.client('cognito-idp', region_name=REGION)

# ============================================================================
# STEP 1: Create User Pool
# ============================================================================
print("Step 1: Creating Cognito User Pool...")
print(f"  Pool Name: {POOL_NAME}")

try:
    user_pool_response = cognito_client.create_user_pool(
        PoolName=POOL_NAME,
        Policies={
            'PasswordPolicy': {
                'MinimumLength': 8,
                'RequireUppercase': False,
                'RequireLowercase': False,
                'RequireNumbers': False,
                'RequireSymbols': False
            }
        },
        AutoVerifiedAttributes=['email'],
        Schema=[
            {
                'Name': 'email',
                'AttributeDataType': 'String',
                'Required': True,
                'Mutable': True
            }
        ]
    )
    
    user_pool_id = user_pool_response['UserPool']['Id']
    print(f"✓ User Pool created: {user_pool_id}")
    
except Exception as e:
    print(f"❌ Error creating user pool: {e}")
    exit(1)

# ============================================================================
# STEP 2: Create Domain Prefix
# ============================================================================
print()
print("Step 2: Creating domain prefix for OAuth endpoints...")
print(f"  Domain Prefix: {DOMAIN_PREFIX}")

try:
    domain_response = cognito_client.create_user_pool_domain(
        Domain=DOMAIN_PREFIX,
        UserPoolId=user_pool_id
    )
    
    print(f"✓ Domain created: {DOMAIN_PREFIX}.auth.{REGION}.amazoncognito.com")
    
except Exception as e:
    print(f"❌ Error creating domain: {e}")
    # Cleanup and exit
    cognito_client.delete_user_pool(UserPoolId=user_pool_id)
    exit(1)

# ============================================================================
# STEP 3: Create Resource Server (for OAuth scopes)
# ============================================================================
print()
print("Step 3: Creating resource server with OAuth scopes...")

try:
    resource_server_response = cognito_client.create_resource_server(
        UserPoolId=user_pool_id,
        Identifier='gateway-api',
        Name='Gateway API',
        Scopes=[
            {
                'ScopeName': 'read',
                'ScopeDescription': 'Read access to gateway'
            },
            {
                'ScopeName': 'write',
                'ScopeDescription': 'Write access to gateway'
            }
        ]
    )
    
    print(f"✓ Resource server created with read/write scopes")
    
except Exception as e:
    print(f"❌ Error creating resource server: {e}")
    # Cleanup
    cognito_client.delete_user_pool_domain(Domain=DOMAIN_PREFIX, UserPoolId=user_pool_id)
    cognito_client.delete_user_pool(UserPoolId=user_pool_id)
    exit(1)

# ============================================================================
# STEP 4: Create App Client (for machine-to-machine auth)
# ============================================================================
print()
print("Step 4: Creating app client for machine-to-machine authentication...")

try:
    app_client_response = cognito_client.create_user_pool_client(
        UserPoolId=user_pool_id,
        ClientName=APP_CLIENT_NAME,
        GenerateSecret=True,  # Required for client credentials flow
        AllowedOAuthFlows=['client_credentials'],
        AllowedOAuthScopes=[
            'gateway-api/read',
            'gateway-api/write'
        ],
        AllowedOAuthFlowsUserPoolClient=True,
        ExplicitAuthFlows=[],  # No user auth flows needed
        SupportedIdentityProviders=[]  # No external identity providers
    )
    
    client_id = app_client_response['UserPoolClient']['ClientId']
    print(f"✓ App client created: {client_id}")
    
except Exception as e:
    print(f"❌ Error creating app client: {e}")
    # Cleanup
    cognito_client.delete_user_pool_domain(Domain=DOMAIN_PREFIX, UserPoolId=user_pool_id)
    cognito_client.delete_user_pool(UserPoolId=user_pool_id)
    exit(1)

# ============================================================================
# STEP 5: Get Client Secret
# ============================================================================
print()
print("Step 5: Retrieving client secret...")

try:
    client_details = cognito_client.describe_user_pool_client(
        UserPoolId=user_pool_id,
        ClientId=client_id
    )
    
    client_secret = client_details['UserPoolClient']['ClientSecret']
    print(f"✓ Client secret retrieved")
    
except Exception as e:
    print(f"❌ Error retrieving client secret: {e}")
    exit(1)

# ============================================================================
# STEP 6: Build Configuration URLs
# ============================================================================
print()
print("Step 6: Building OAuth endpoint URLs...")

# Token endpoint (for getting access tokens)
token_endpoint = f"https://{DOMAIN_PREFIX}.auth.{REGION}.amazoncognito.com/oauth2/token"

# CRITICAL: Use IDP-based discovery URL (NOT hosted UI domain)
discovery_url = f"https://cognito-idp.{REGION}.amazonaws.com/{user_pool_id}/.well-known/openid-configuration"

print(f"✓ Token endpoint: {token_endpoint}")
print(f"✓ Discovery URL: {discovery_url}")

# ============================================================================
# STEP 7: Save Configuration
# ============================================================================
print()
print("Step 7: Saving configuration to cognito_config.json...")

config = {
    "user_pool_id": user_pool_id,
    "domain_prefix": DOMAIN_PREFIX,
    "client_id": client_id,
    "client_secret": client_secret,
    "token_endpoint": token_endpoint,
    "discovery_url": discovery_url,
    "region": REGION
}

try:
    with open('cognito_config.json', 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"✓ Configuration saved to cognito_config.json")
    
except Exception as e:
    print(f"❌ Error saving configuration: {e}")
    exit(1)

# ============================================================================
# SUMMARY
# ============================================================================
print()
print("=" * 80)
print("COGNITO SETUP COMPLETE")
print("=" * 80)
print()
print(f"User Pool ID: {user_pool_id}")
print(f"Domain Prefix: {DOMAIN_PREFIX}")
print(f"Client ID: {client_id}")
print(f"Client Secret: {client_secret[:10]}...")
print()
print("OAuth Scopes: gateway-api/read, gateway-api/write")
print()
print("Configuration saved to: cognito_config.json")
print()
print("This Cognito setup provides:")
print("  ✓ Secure authentication for gateway access")
print("  ✓ Machine-to-machine OAuth2 client credentials flow")
print("  ✓ Read/write permissions for gateway operations")
print("=" * 80)
