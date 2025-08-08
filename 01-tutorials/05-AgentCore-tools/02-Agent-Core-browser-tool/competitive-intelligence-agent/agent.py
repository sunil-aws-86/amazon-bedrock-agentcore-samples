"""Main LangGraph agent for competitive intelligence gathering."""

import asyncio
import sys
from pathlib import Path
from typing import Dict, List, TypedDict, Annotated, Optional
from datetime import datetime

from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_aws import ChatBedrockConverse
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn

# Add parent directory to path to import from interactive_tools
sys.path.append(str(Path(__file__).parent.parent))

# Import our tools
from config import AgentConfig
from browser_tools import BrowserTools
from analysis_tools import AnalysisTools

# Import browser viewer from interactive_tools
from interactive_tools.browser_viewer import BrowserViewerServer

console = Console()


class CompetitiveIntelState(TypedDict):
    """State for the competitive intelligence agent."""
    messages: Annotated[List, "append"]
    competitors: List[Dict]
    current_competitor_index: int
    competitor_data: Dict
    analysis_results: Dict
    report: Optional[str]
    recording_path: Optional[str]
    error: Optional[str]
    total_screenshots: int
    discovered_apis: List[Dict]
    performance_metrics: Dict


class CompetitiveIntelligenceAgent:
    """LangGraph agent for competitive intelligence gathering."""
    
    def __init__(self, config: AgentConfig):
        self.config = config
        self.browser_tools = BrowserTools(config)
        self.analysis_tools = AnalysisTools(config)
        self.llm = None
        self.graph = None
        self.browser_viewer = None
    
    async def initialize(self):
        """Initialize the agent and its tools."""
        console.print(Panel(
            "[bold cyan]🎯 Competitive Intelligence Agent[/bold cyan]\n\n"
            "[bold]Powered by Amazon Bedrock AgentCore[/bold]\n\n"
            "Features:\n"
            "• 🌐 Automated browser navigation\n"
            "• 📊 Real-time API and network analysis\n"
            "• 🎯 Intelligent content extraction\n"
            "• 📸 Screenshot capture\n"
            "• 📹 Full session recording to S3\n",
            title="Initializing",
            border_style="blue"
        ))
        
        # Initialize browser with recording
        self.browser_tools.create_browser_with_recording()
        
        # Initialize LLM
        self.llm = ChatBedrockConverse(
            model_id=self.config.llm_model_id,
            region_name=self.config.region
        )
        console.print(f"✅ LLM initialized: {self.config.llm_model_id}")
        
        # Initialize browser session with CDP
        await self.browser_tools.initialize_browser_session(self.llm)
        
        # Initialize code interpreter
        self.analysis_tools.initialize()
        
        # Start browser live viewer
        if self.browser_tools.browser_client:
            console.print("\n[cyan]🖥️ Starting live browser viewer...[/cyan]")
            self.browser_viewer = BrowserViewerServer(
                self.browser_tools.browser_client, 
                port=self.config.live_view_port
            )
            viewer_url = self.browser_viewer.start(open_browser=True)
            console.print(f"[green]✅ Live viewer: {viewer_url}[/green]")
            console.print("[dim]You can take/release control in the viewer[/dim]")
        
        # Build the graph
        self._build_graph()
        
        console.print("\n[green]✅ Agent initialized successfully![/green]")
        console.print(f"[cyan]📹 Recording to: {self.browser_tools.recording_path}[/cyan]")
    
    def _build_graph(self):
        """Build the LangGraph workflow."""
        workflow = StateGraph(CompetitiveIntelState)
        
        # Add nodes
        workflow.add_node("analyze_competitor", self.analyze_competitor)
        workflow.add_node("process_data", self.process_data)
        workflow.add_node("generate_report", self.generate_report)
        
        # Set entry point
        workflow.set_entry_point("analyze_competitor")
        
        # Conditional edge to loop through competitors
        workflow.add_conditional_edges(
            "analyze_competitor",
            self.should_continue_analyzing,
            {
                "continue": "analyze_competitor",
                "process": "process_data"
            }
        )
        
        workflow.add_edge("process_data", "generate_report")
        workflow.add_edge("generate_report", END)
        
        self.graph = workflow.compile()
    
# Update the analyze_competitor method in agent.py to use the new features:

    async def analyze_competitor(self, state: CompetitiveIntelState) -> CompetitiveIntelState:
        """Analyze a single competitor with enhanced features."""
        competitors = state["competitors"]
        current_index = state.get("current_competitor_index", 0)
        
        if current_index >= len(competitors):
            return state
        
        competitor = competitors[current_index]
        console.print(f"\n[bold blue]🔍 Analyzing Competitor {current_index + 1}/{len(competitors)}: {competitor['name']}[/bold blue]")
        
        # Progress tracking
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            console=console
        ) as progress:
            task = progress.add_task(f"Analyzing {competitor['name']}...", total=8)
            
            competitor_data = {}
            
            try:
                # Step 1: Navigate
                progress.update(task, description="Navigating to website...", advance=1)
                nav_result = await self.browser_tools.navigate_to_url(competitor['url'])
                competitor_data['navigation'] = nav_result
                
                # Step 2: Take initial screenshot
                progress.update(task, description="Taking homepage screenshot...", advance=1)
                try:
                    await self.browser_tools.take_annotated_screenshot(f"{competitor['name']} - Homepage")
                except Exception as e:
                    console.print(f"[yellow]⚠️ Screenshot error: {e}[/yellow]")
                
                # Step 3: Intelligent discovery - NEW!
                progress.update(task, description="Discovering page sections...", advance=1)
                try:
                    discovered_sections = await self.browser_tools.intelligent_scroll_and_discover()
                    competitor_data['discovered_sections'] = discovered_sections
                    console.print(f"[green]Found {len(discovered_sections)} key sections[/green]")
                except Exception as e:
                    console.print(f"[yellow]⚠️ Discovery error: {e}[/yellow]")
                    competitor_data['discovered_sections'] = []
                
                # Step 4: Try to navigate to pricing page - NEW!
                progress.update(task, description="Looking for pricing page...", advance=1)
                try:
                    found_pricing = await self.browser_tools.smart_navigation("pricing")
                    if found_pricing:
                        await asyncio.sleep(3)  # Let page load
                        await self.browser_tools.take_annotated_screenshot(f"{competitor['name']} - Pricing Page")
                except Exception as e:
                    console.print(f"[yellow]⚠️ Navigation error: {e}[/yellow]")
                
                # Step 5: Extract pricing
                progress.update(task, description="Extracting pricing information...", advance=1)
                try:
                    pricing_result = await self.browser_tools.extract_pricing_info()
                    competitor_data['pricing'] = pricing_result
                except Exception as e:
                    console.print(f"[yellow]⚠️ Pricing extraction error: {e}[/yellow]")
                    competitor_data['pricing'] = {"status": "error", "error": str(e)}
                
                # Step 6: Extract features
                progress.update(task, description="Extracting product features...", advance=1)
                try:
                    features_result = await self.browser_tools.extract_product_features()
                    competitor_data['features'] = features_result
                except Exception as e:
                    console.print(f"[yellow]⚠️ Feature extraction error: {e}[/yellow]")
                    competitor_data['features'] = {"status": "error", "error": str(e)}
                
                # Step 7: Capture performance metrics - NEW!
                progress.update(task, description="Capturing performance metrics...", advance=1)
                try:
                    metrics = await self.browser_tools.capture_performance_metrics()
                    competitor_data['performance_metrics'] = metrics
                except Exception as e:
                    console.print(f"[yellow]⚠️ Metrics error: {e}[/yellow]")
                
                # Step 8: Final screenshot
                progress.update(task, description="Taking final screenshot...", advance=1)
                try:
                    await self.browser_tools.take_annotated_screenshot(f"{competitor['name']} - Analysis Complete")
                except Exception as e:
                    console.print(f"[yellow]⚠️ Final screenshot error: {e}[/yellow]")
            
            except Exception as e:
                console.print(f"[red]❌ Critical error analyzing {competitor['name']}: {e}[/red]")
                competitor_data = {
                    "status": "error",
                    "error": str(e),
                    "url": competitor['url']
                }
        
        # Store results
        all_competitor_data = state.get("competitor_data", {})
        all_competitor_data[competitor['name']] = {
            "url": competitor['url'],
            "timestamp": datetime.now().isoformat(),
            **competitor_data,
            "apis_discovered": len(self.browser_tools._discovered_apis),
            "screenshots_taken": len(self.browser_tools._screenshots_taken),
            "status": "success" if competitor_data.get("navigation", {}).get("status") == "success" else "error"
        }
        
        # Analyze this competitor's data
        console.print(f"[cyan]📊 Running analysis for {competitor['name']}...[/cyan]")
        try:
            analysis_result = self.analysis_tools.analyze_competitor_data(
                competitor['name'], 
                all_competitor_data[competitor['name']]
            )
        except Exception as e:
            console.print(f"[yellow]⚠️ Analysis error: {e}[/yellow]")
            analysis_result = {"status": "error", "error": str(e)}
        
        console.print(f"[green]✅ Completed: {competitor['name']}[/green]")
        console.print(f"  • Discovered {len(competitor_data.get('discovered_sections', []))} sections")
        console.print(f"  • Found {len(self.browser_tools._discovered_apis)} API endpoints")
        console.print(f"  • Took {len(self.browser_tools._screenshots_taken)} screenshots")
        
        # Update state
        return {
            **state,
            "current_competitor_index": current_index + 1,
            "competitor_data": all_competitor_data,
            "total_screenshots": state.get("total_screenshots", 0) + len(self.browser_tools._screenshots_taken),
            "discovered_apis": state.get("discovered_apis", []) + self.browser_tools._discovered_apis,
            "messages": state["messages"] + [
                HumanMessage(content=f"Analyzed {competitor['name']}: {analysis_result}")
            ]
        }
    
    def should_continue_analyzing(self, state: CompetitiveIntelState) -> str:
        """Determine if we should continue to the next competitor."""
        current_index = state.get("current_competitor_index", 0)
        total_competitors = len(state["competitors"])
        
        if current_index < total_competitors:
            return "continue"
        else:
            return "process"
    
    async def process_data(self, state: CompetitiveIntelState) -> CompetitiveIntelState:
        """Process all collected data and create visualizations."""
        console.print("\n[bold yellow]📊 Processing all competitor data...[/bold yellow]")
        
        competitor_data = state.get("competitor_data", {})
        
        # Create comparison visualization
        console.print("[cyan]Creating visualizations...[/cyan]")
        viz_result = self.analysis_tools.create_comparison_visualization(competitor_data)
        
        # List all generated files
        #files_result = self.analysis_tools.list_generated_files()
        
        #console.print(f"[green]✅ Created {files_result.get('count', 0)} analysis files[/green]")
        
        return {
            **state,
            "analysis_results": {
                "visualization": viz_result,
#                "files": files_result,
                "total_competitors": len(competitor_data),
                "successful_analyses": sum(1 for d in competitor_data.values() if d.get('status') == 'success'),
                "total_apis_discovered": len(state.get("discovered_apis", []))
            }
        }
    
    async def generate_report(self, state: CompetitiveIntelState) -> CompetitiveIntelState:
        """Generate the final report."""
        console.print("\n[bold green]📄 Generating final report...[/bold green]")
        
        # Generate comprehensive report
        report_result = self.analysis_tools.generate_final_report(
            state.get("competitor_data", {}),
            state.get("analysis_results", {})
        )
        
        # Get recording path
        recording_path = self.browser_tools.recording_path
        
        # Summary panel
        console.print("\n")
        console.print(Panel(
            f"[bold green]✅ Analysis Complete![/bold green]\n\n"
            f"📊 Competitors analyzed: {len(state['competitors'])}\n"
            f"📸 Screenshots taken: {state.get('total_screenshots', 0)}\n"
            f"🔍 APIs discovered: {len(state.get('discovered_apis', []))}\n"
            f"📄 Report: {report_result.get('report_path', 'N/A')}\n"
            f"📹 Recording: {recording_path}\n",
#            f"📁 Files generated: {state['analysis_results']['files']['count']}",
            title="Summary",
            border_style="green"
        ))
        
        return {
            **state,
            "report": report_result.get("report_content", ""),
            "recording_path": recording_path,
            "messages": state["messages"] + [
                HumanMessage(content=f"Report generated: {report_result.get('output', '')}")
            ]
        }
    
    async def run(self, competitors: List[Dict]) -> Dict:
        """Run the competitive intelligence analysis."""
        try:
            # Initialize state
            initial_state: CompetitiveIntelState = {
                "messages": [SystemMessage(content="Starting competitive intelligence analysis")],
                "competitors": competitors,
                "current_competitor_index": 0,
                "competitor_data": {},
                "analysis_results": {},
                "report": None,
                "recording_path": None,
                "error": None,
                "total_screenshots": 0,
                "discovered_apis": [],
                "performance_metrics": {}
            }
            
            # Run the graph
            console.print("\n[cyan]🚀 Starting analysis workflow...[/cyan]")
            final_state = await self.graph.ainvoke(initial_state)
            
            return {
                "success": True,
                "report": final_state["report"],
                "recording_path": final_state["recording_path"],
                "analysis_results": final_state["analysis_results"],
#                "files": final_state["analysis_results"]["files"]["files"],
                "apis_discovered": final_state.get("discovered_apis", [])
            }
            
        except Exception as e:
            console.print(f"[red]❌ Agent error: {e}[/red]")
            import traceback
            traceback.print_exc()
            return {"success": False, "error": str(e)}
    
    async def cleanup(self):
        """Clean up agent resources."""
        console.print("\n[yellow]🧹 Cleaning up...[/yellow]")
        
        # Cleanup browser
        await self.browser_tools.cleanup()
        
        # Cleanup code interpreter
        self.analysis_tools.cleanup()
        
        console.print("[green]✅ Cleanup complete[/green]")