"""Browser automation script using Amazon Bedrock AgentCore and Nova Act.

This script demonstrates AI-powered web automation by:
- Initializing a browser session through Amazon Bedrock AgentCore
- Connecting to Nova Act for natural language web interactions
- Performing automated searches and data extraction using browser
"""

from bedrock_agentcore.tools.browser_client import browser_session
from nova_act import NovaAct
from rich.console import Console
import time

NOVA_ACT_API_KEY = "xxxx"  # Replace with your actual Nova Act API key

console = Console()


def main():
    with browser_session("us-west-2") as client:
        console.print("[cyan]Step 1: Waiting for browser initialization...[/cyan]")
        console.print("[dim]This 20-second wait is required for now..")
        for i in range(20, 0, -1):
            print(f"\r   {i} seconds remaining...", end="", flush=True)
            time.sleep(1)
        console.print("\r   Browser ready!                    ")
        ws_url, headers = client.generate_ws_headers()

        try:
            with NovaAct(
                cdp_endpoint_url=ws_url,
                cdp_headers=headers,
                preview={"playwright_actuation": True},
                nova_act_api_key=NOVA_ACT_API_KEY,
                starting_page="https://www.amazon.com",
            ) as nova_act:
                result = nova_act.act(
                    "Search for a coffee maker and extract the details of the first result."
                )
        except Exception as e:
            console.print(f"NovaAct error: {e}")
        return result


if __name__ == "__main__":
    try:
        result = main()
        console.print("Nova Act Result:", result)
    except Exception as e:
        console.print(f"Error in Nova Act execution: {e}")
