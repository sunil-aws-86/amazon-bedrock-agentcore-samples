#!/usr/bin/env python3
"""Run the Competitive Intelligence Agent with AWS-focused examples."""

import asyncio
import os
import sys
from pathlib import Path
from typing import List, Dict

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.table import Table
from rich.panel import Panel

from config import AgentConfig
from agent import CompetitiveIntelligenceAgent
from utils.s3_datasource import UnifiedS3DataSource
from interactive_tools.live_view_sessionreplay.session_replay_viewer import SessionReplayViewer

console = Console()


def get_bedrock_agentcore_single() -> List[Dict]:
    """Analyze AWS Bedrock AgentCore pricing."""
    return [
        {
            "name": "AWS Bedrock AgentCore",
            "url": "https://aws.amazon.com/bedrock/agentcore/pricing/",
            "analyze": ["pricing", "features", "models", "regions"]
        }
    ]


def get_bedrock_vs_vertex() -> List[Dict]:
    """Compare AWS Bedrock AgentCore with Google Vertex AI."""
    return [
        {
            "name": "AWS Bedrock AgentCore",
            "url": "https://aws.amazon.com/bedrock/agentcore/pricing/",
            "analyze": ["pricing", "features", "models", "regions"]
        },
        {
            "name": "Google Vertex AI",
            "url": "https://cloud.google.com/vertex-ai/pricing",
            "analyze": ["pricing", "features", "models", "apis"]
        }
    ]


def get_custom_competitors() -> List[Dict]:
    """Get custom competitors from user input."""
    competitors = []
    
    console.print("\n[bold]Enter competitors to analyze:[/bold]")
    console.print("[dim]Press Enter with empty name to finish[/dim]\n")
    
    while True:
        name = Prompt.ask("Competitor name", default="")
        if not name:
            break
            
        url = Prompt.ask(f"URL for {name}")
        
        # Auto-detect what to analyze based on URL
        analyze = ["pricing", "features"]
        if "pricing" in url.lower() or "price" in url.lower():
            analyze.append("tiers")
        if "api" in url.lower():
            analyze.append("apis")
        
        competitors.append({
            "name": name,
            "url": url,
            "analyze": analyze
        })
        
        console.print(f"[green]✓ Added {name}[/green]\n")
    
    return competitors


def show_competitors_table(competitors: List[Dict]):
    """Display competitors in a table."""
    table = Table(title="Competitors to Analyze", title_style="bold cyan")
    table.add_column("#", style="cyan", width=4)
    table.add_column("Name", style="magenta")
    table.add_column("URL", style="blue")
    table.add_column("Analysis Focus", style="green")
    
    for i, comp in enumerate(competitors, 1):
        table.add_row(
            str(i),
            comp['name'],
            comp['url'][:50] + "..." if len(comp['url']) > 50 else comp['url'],
            ", ".join(comp.get('analyze', []))
        )
    
    console.print(table)


async def view_replay(recording_path: str, config: AgentConfig):
    """
    Start the session replay viewer using the unified S3 data source.
    This consolidates all the fixes from your working code.
    """
    try:
        console.print("\n[cyan]🎭 Starting session replay viewer...[/cyan]")
        
        # Parse S3 path correctly
        # Example: s3://bucket/competitive_intel/SESSION_ID/
        parts = recording_path.replace("s3://", "").rstrip("/").split("/")
        bucket = parts[0]
        
        if len(parts) >= 3:
            # Typical case: bucket/competitive_intel/SESSION_ID
            prefix = parts[1]  
            session_id = parts[2]  # The session ID
        elif len(parts) == 2:
            # Edge case: bucket/SESSION_ID
            prefix = ""
            session_id = parts[1]
        else:
            # Fallback
            prefix = ""
            session_id = parts[-1] if len(parts) > 1 else "unknown"
        
        console.print(f"[dim]Bucket: {bucket}[/dim]")
        console.print(f"[dim]Prefix: {prefix}[/dim]")
        console.print(f"[dim]Session: {session_id}[/dim]")
        
        # Wait for recordings to be uploaded
        console.print("⏳ Waiting for recordings to be uploaded to S3 (30 seconds)...")
        await asyncio.sleep(30)
        
        # Use the unified S3 data source with corrected parameters
        data_source = UnifiedS3DataSource(bucket=bucket, prefix=prefix, session_id=session_id)
        
        # Start replay viewer
        console.print(f"🎬 Starting session replay viewer for: {session_id}")
        viewer = SessionReplayViewer(data_source=data_source, port=config.replay_viewer_port)
        viewer.start()  # This will block until Ctrl+C
        
    except Exception as e:
        console.print(f"[red]❌ Error starting replay viewer: {e}[/red]")
        import traceback
        traceback.print_exc()

async def main():
    """Main function to run the agent."""
    console.print(Panel(
        "[bold cyan]🎯 Competitive Intelligence Agent[/bold cyan]\n\n"
        "[bold]Powered by Amazon Bedrock AgentCore[/bold]\n\n"
        "Features:\n"
        "• 🔍 Automated browser navigation with CDP\n"
        "• 📊 Intelligent content extraction with LLM\n"
        "• 📸 Screenshot capture with annotations\n"
        "• 📹 Full session recording to S3\n"
        "• 🎭 Session replay capability\n"
        "• 🤖 Claude 3.5 Sonnet for analysis",
        title="Welcome",
        border_style="blue"
    ))
    
    # Load configuration
    config = AgentConfig()
    
    # Validate configuration
    if not config.validate():
        console.print("[red]❌ Configuration validation failed[/red]")
        console.print("Please set the following environment variables:")
        console.print("  - AWS_REGION (or use default us-west-2)")
        console.print("  - RECORDING_ROLE_ARN (or set AWS_ACCOUNT_ID for default)")
        console.print("  - S3_RECORDING_BUCKET (optional)")
        console.print("  - S3_RECORDING_PREFIX (optional)")
        return
    
    # Show configuration
    console.print("\n[bold]Configuration:[/bold]")
    console.print(f"  Region: {config.region}")
    console.print(f"  Model: {config.llm_model_id}")
    console.print(f"  S3 Bucket: {config.s3_bucket}")
    console.print(f"  S3 Prefix: {config.s3_prefix}")
    console.print(f"  Role ARN: {config.recording_role_arn}")
    console.print()
    
    # Get competitors
    console.print("\n[bold]Select analysis option:[/bold]")
    console.print("1. 🎯 AWS Bedrock AgentCore Pricing Only")
    console.print("2. 🆚 Compare Bedrock AgentCore vs Vertex AI")
    console.print("3. ✏️  Custom competitors")
    
    choice = Prompt.ask("Select option", choices=["1", "2", "3"], default="1")
    
    if choice == "1":
        competitors = get_bedrock_agentcore_single()
    elif choice == "2":
        competitors = get_bedrock_vs_vertex()
    else:
        competitors = get_custom_competitors()
        if not competitors:
            console.print("[yellow]No competitors entered. Exiting.[/yellow]")
            return
    
    # Show competitors
    show_competitors_table(competitors)
    
    if not Confirm.ask("\nProceed with analysis?", default=True):
        console.print("[yellow]Analysis cancelled.[/yellow]")
        return
    
    # Create and run agent
    agent = CompetitiveIntelligenceAgent(config)
    
    try:
        # Initialize
        await agent.initialize()
        
        # Show what to watch for
        watch_panel = Panel(
            "[bold yellow]👁️  Watch the Live Browser Viewer![/bold yellow]\n\n"
            "[bold]The browser will automatically:[/bold]\n"
            "• Navigate to each competitor's pricing page\n"
            "• Scroll through pages to discover content\n"
            "• Extract pricing information and features\n"
            "• Take annotated screenshots\n"
            "• Track API endpoints\n"
            "• Generate a comprehensive report\n\n"
            "[dim]You can take manual control at any time using the viewer controls[/dim]",
            border_style="yellow"
        )
        console.print(watch_panel)
        
        console.print("\n[cyan]Starting automated analysis in 5 seconds...[/cyan]")
        console.print("[dim]Open the browser viewer link above to watch the automation![/dim]")
        await asyncio.sleep(5)
        
        # Run analysis
        results = await agent.run(competitors)
        
        if results["success"]:
            # Show results summary
            results_panel = Panel(
                f"[bold green]✅ Analysis Complete![/bold green]\n\n"
                f"[bold]Key Findings:[/bold]\n"
                f"📊 Competitors analyzed: {len(competitors)}\n"
                f"📸 Screenshots captured: {results.get('analysis_results', {}).get('total_screenshots', 0)}\n"
                f"🌐 API endpoints discovered: {len(results.get('apis_discovered', []))}\n"
                f"📄 Report generated: Yes\n"
                f"📹 Session recorded: Yes",
                border_style="green"
            )
            console.print(results_panel)
            
            # Show report preview
            if results.get("report"):
                console.print("\n[bold]Report Preview:[/bold]")
                console.print("-" * 60)
                preview = results['report'][:1500]
                console.print(preview + "..." if len(results['report']) > 1500 else preview)
                console.print("-" * 60)
            
            # Show discovered APIs if any
            if results.get("apis_discovered"):
                console.print("\n[bold]Discovered API Endpoints:[/bold]")
                for api in results["apis_discovered"][:5]:  # Show first 5
                    console.print(f"  • {api['url'][:80]}...")
                if len(results["apis_discovered"]) > 5:
                    console.print(f"  ... and {len(results['apis_discovered']) - 5} more")
            
            # Ask about replay
            if results.get("recording_path"):
                replay_prompt = Panel(
                    "[bold cyan]🎬 Session Recording Available![/bold cyan]\n\n"
                    "Your entire analysis session has been recorded.\n"
                    "You can replay it to:\n"
                    "• Review the extraction process\n"
                    "• Share findings with stakeholders\n"
                    "• Debug any issues\n"
                    "• Create training materials",
                    border_style="cyan"
                )
                console.print(replay_prompt)
                
                if Confirm.ask("\nView session replay?", default=True):
                    await view_replay(results["recording_path"], config)
        else:
            console.print(f"\n[red]Analysis failed: {results.get('error', 'Unknown error')}[/red]")
    
    except KeyboardInterrupt:
        console.print("\n[yellow]Analysis interrupted by user[/yellow]")
    except Exception as e:
        console.print(f"\n[red]Unexpected error: {e}[/red]")
        import traceback
        traceback.print_exc()
    finally:
        # Always cleanup
        await agent.cleanup()
        console.print("\n[green]✅ Agent shutdown complete[/green]")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupted by user[/yellow]")
    except Exception as e:
        console.print(f"\n[red]Unexpected error: {e}[/red]")
        import traceback
        traceback.print_exc()