#!/usr/bin/env python3
"""
Generate architecture diagram for Returns & Refunds Agent.

This script creates a visual representation of the complete system architecture
using the diagrams library with AWS icons.
"""

try:
    from diagrams import Diagram, Cluster, Edge
    from diagrams.aws.compute import Lambda
    from diagrams.aws.ml import Bedrock
    from diagrams.aws.security import Cognito, IAM
    from diagrams.aws.integration import SimpleNotificationServiceSns as Gateway
    from diagrams.aws.database import Database
    from diagrams.aws.storage import S3
    from diagrams.custom import Custom
    import os
except ImportError:
    print("Installing required packages...")
    import subprocess
    subprocess.check_call(["pip", "install", "diagrams", "graphviz"])
    print("\nPackages installed. Please run the script again.")
    exit(0)

# Set diagram attributes
graph_attr = {
    "fontsize": "14",
    "bgcolor": "white",
    "pad": "0.5",
    "splines": "ortho",
    "nodesep": "0.8",
    "ranksep": "1.0"
}

node_attr = {
    "fontsize": "12",
    "height": "1.2",
    "width": "1.2"
}

edge_attr = {
    "fontsize": "10"
}

print("Generating architecture diagram...")

with Diagram(
    "Returns & Refunds Agent - Complete Architecture",
    filename="architecture_diagram",
    show=False,
    direction="TB",
    graph_attr=graph_attr,
    node_attr=node_attr,
    edge_attr=edge_attr
):
    
    # User/Customer
    user = Custom("Customer\n(user_001)", "./user_icon.png") if os.path.exists("./user_icon.png") else Database("Customer\n(user_001)")
    
    with Cluster("Strands Agent\n(full_featured_returns_agent)"):
        agent = Bedrock("Returns Agent\n\nMemory + Gateway\n+ Knowledge Base\n+ Custom Tools")
        
        with Cluster("Built-in Tools"):
            current_time = Lambda("current_time")
            retrieve = Lambda("retrieve")
        
        with Cluster("Custom Tools"):
            check_eligibility = Lambda("check_return\n_eligibility")
            calc_refund = Lambda("calculate\n_refund_amount")
            format_policy = Lambda("format_policy\n_response")
    
    with Cluster("AgentCore Memory\n(returns_refunds_memory-p7dffNC0ha)"):
        memory_service = Database("Memory Service")
        
        with Cluster("Memory Namespaces"):
            preferences = S3("Preferences\napp/{actorId}/\npreferences")
            semantic = S3("Semantic\napp/{actorId}/\nsemantic")
            summary = S3("Summary\napp/{actorId}/\n{sessionId}/summary")
    
    with Cluster("Knowledge Base\n(XWCNYZDEGT)"):
        kb = Database("Bedrock\nKnowledge Base\n\nAmazon Return\nPolicies")
    
    with Cluster("AgentCore Gateway\n(returnsrefundsgateway-q6skfjrtth)"):
        with Cluster("Authentication"):
            cognito = Cognito("Cognito\nUser Pool\n\nus-west-2_jblrQsfU3\n\nOAuth2 Client\nCredentials")
        
        gateway = Gateway("MCP Gateway\n\nProtocol: MCP\nAuth: JWT")
        
        with Cluster("IAM"):
            gateway_role = IAM("Gateway Role\n\nLambda Invoke\nPermissions")
        
        with Cluster("Gateway Targets"):
            lambda_target = Lambda("OrderLookup\nTarget\n\nlookup_order")
    
    with Cluster("Lambda Function\n(OrderLookupFunction)"):
        order_lambda = Lambda("Order Lookup\nLambda\n\nPython 3.12")
        
        with Cluster("Mock Order Database"):
            ord1 = Database("ORD-001\nLaptop\n$1,299.99\n✓ Eligible")
            ord2 = Database("ORD-002\niPhone\n$799.99\n✗ Not Eligible")
            ord3 = Database("ORD-003\nTablet\n$449.99\n✓ Eligible")
    
    # Main flow
    user >> Edge(label="Query:\nLook up ORD-001") >> agent
    
    # Agent to Memory
    agent >> Edge(label="Retrieve\nPreferences") >> memory_service
    memory_service >> preferences
    memory_service >> semantic
    memory_service >> summary
    
    # Agent to Knowledge Base
    agent >> Edge(label="Search\nPolicies") >> kb
    
    # Agent to Gateway
    agent >> Edge(label="Request\nAccess Token") >> cognito
    cognito >> Edge(label="JWT Token") >> agent
    agent >> Edge(label="lookup_order\n(ORD-001)") >> gateway
    
    # Gateway flow
    gateway >> gateway_role
    gateway >> lambda_target
    lambda_target >> Edge(label="Invoke") >> order_lambda
    
    # Lambda to data
    order_lambda >> ord1
    order_lambda >> ord2
    order_lambda >> ord3
    
    # Response flow
    order_lambda >> Edge(label="Order Details\n+ Eligibility", style="dashed") >> lambda_target
    lambda_target >> Edge(label="Response", style="dashed") >> gateway
    gateway >> Edge(label="Tool Result", style="dashed") >> agent
    
    # Agent uses custom tools
    agent >> check_eligibility
    agent >> calc_refund
    agent >> format_policy
    
    # Final response
    agent >> Edge(label="Personalized\nResponse", style="bold") >> user

print("✓ Diagram generated: architecture_diagram.png")
print()
print("The diagram shows:")
print("  • Customer query flow")
print("  • Memory integration (3 namespaces)")
print("  • Gateway authentication (Cognito)")
print("  • Lambda invocation via gateway")
print("  • Custom tools integration")
print("  • Complete response flow")
print()
print("Open 'architecture_diagram.png' to view the diagram.")
