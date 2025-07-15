import httpx
import os
from dotenv import load_dotenv
import boto3
import requests
import subprocess
import json

#Reading environment variables
load_dotenv()

def create_agentcore_client():
    #create boto3 session and client
    if os.getenv("awscred_profile_name") is None:
        boto_session = boto3.Session() #using default profile
    else:
        boto_session = boto3.Session(profile_name=os.getenv("awscred_profile_name"))

    agentcore_client = boto_session.client(
        "bedrock-agentcore-control",
        region_name=os.getenv("aws_default_region"),
        endpoint_url=os.getenv("agentcore_cp_base_url")
    )

    return boto_session, agentcore_client

def create_http_client(**kwargs) -> httpx.AsyncClient:
    """Create an HTTPX client with SSL verification disabled."""
    kwargs['verify'] = False
    # Optionally add other configurations
    kwargs.setdefault('timeout', httpx.Timeout(30.0))
    return httpx.AsyncClient(**kwargs)

def get_gateway_endpoint(agentcore_client, gateway_id):
    response = agentcore_client.get_gateway(
        gatewayIdentifier=gateway_id\
    )

    return response['gatewayUrl']

def list_gateways(agentcore_client):
    response = agentcore_client.list_gateways()

    return response['items']

def list_egress_oauth_providers():
    try:
        command = [
            "aws", "acps", "list-oauth2-credential-providers",
            "--endpoint-url", os.getenv("identity_base_url"),
            "--region", "us-east-1"
        ]

        if os.getenv("awscred_profile_name") is not None:
            command.append("--profile")
            command.append(os.getenv("awscred_profile_name"))

        result = subprocess.run(command, capture_output=True, text=True, check=True)
        return json.loads(result.stdout)
    except Exception as e:
        print(f"An error ocurred: {e}")

def get_oath_token():
    response = requests.post(
        os.getenv("cognito_token_url"),
        data=f"grant_type=client_credentials&client_id={os.getenv('cognito_client_id')}&client_secret={os.getenv('cognito_client_secret')}&scope={os.getenv('cognito_auth_scope')}",
        headers={'Content-Type': 'application/x-www-form-urlencoded'}
    )

    #print(response.json())
    return response.json()['access_token']