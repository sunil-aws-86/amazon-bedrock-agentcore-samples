"""
Live Browser Viewer with Nova Act Integration

Demonstrates real-time browser viewing using AWS Bedrock AgentCore Browser tool
with Nova Act AI agent automation. Features live display streaming, configurable
viewport sizes, and natural language browser control.
"""

import time
from pathlib import Path
from bedrock_agentcore.tools.browser_client import browser_session
from nova_act import NovaAct
from rich.console import Console
from rich.panel import Panel
from interactive_tools.browser_viewer import BrowserViewerServer

console = Console()
NOVA_ACT_API_KEY = "xxxx"  # Replace with your actual Nova Act API key


def main():
    """Run the browser live viewer with display sizing."""
    console.print(
        Panel(
            "[bold cyan] Browser Live Viewer[/bold cyan]\n\n"
            "This demonstrates:\n"
            "• Live browser viewing with DCV\n"
            "• Configurable display sizes (not limited to 900×800)\n"
            "• Proper display layout callbacks\n\n"
            "[yellow]Note: Requires Amazon DCV SDK files[/yellow]",
            title="Browser Live Viewer",
            border_style="blue",
        )
    )

    try:
        # Step 1: Create browser session
        with browser_session("us-west-2") as client:
            console.print(
                "\n[cyan]Step 2: Waiting for browser initialization...[/cyan]"
            )
            console.print("[dim]This 10-second wait is required for now..")
            for i in range(10, 0, -1):
                print(f"\r   {i} seconds remaining...", end="", flush=True)
                time.sleep(1)
            print("\r   ✅ Browser ready!                    ")
            ws_url, headers = client.generate_ws_headers()

            # Step 2: Start viewer server
            console.print("\n[cyan]Step 3: Starting viewer server...[/cyan]")
            viewer = BrowserViewerServer(client, port=8008)
            viewer_url = viewer.start(open_browser=True)

            # Step 3: Show features
            console.print("\n[bold green]Viewer Features:[/bold green]")
            console.print(
                "• Default display: 1600×900 (configured via displayLayout callback)"
            )
            console.print("• Size options: 720p, 900p, 1080p, 1440p")
            console.print("• Real-time display updates")
            console.print("• Take/Release control functionality")

            console.print("\n[yellow]Press Ctrl+C to stop[/yellow]")

            # Step 4: Use Nova Act to interact with the browser
            with NovaAct(
                cdp_endpoint_url=ws_url,
                cdp_headers=headers,
                preview={"playwright_actuation": True},
                nova_act_api_key=NOVA_ACT_API_KEY,
                starting_page="https://www.amazon.com",
            ) as nova_act:
                # nova_act.page.set_viewport_size({"width": 1600, "height": 900})
                result = nova_act.act(
                    "Search for coffee maker and get the details of the lowest priced one on the first page"
                )
                console.print(f"\n[bold green]Nova Act Result:[/bold green] {result}")

            # Keep running
            while True:
                time.sleep(1)

    except KeyboardInterrupt:
        console.print("\n\n[yellow]Shutting down...[/yellow]")
        if "client" in locals():
            client.stop()
            console.print("✅ Browser session terminated")
    except Exception as e:
        console.print(f"\n[red]Error: {e}[/red]")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
