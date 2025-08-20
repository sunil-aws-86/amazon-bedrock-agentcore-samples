"""
Import helper for competitive intelligence agent.
Ensures that interactive_tools can be imported from tutorials.
"""
import sys
import os
from pathlib import Path

def setup_interactive_tools_import():
    """
    Add the tutorials directory to Python path to ensure
    interactive_tools can be imported correctly.
    """
    # Get the current file's directory
    current_dir = Path(__file__).parent.parent  # utils/ -> competitive-intelligence-agent/
    
    # Go up to the repo root
    repo_root = current_dir.parent.parent  # 02-use-cases/ -> repo root
    
    # Add the tutorials directory to path
    tutorials_path = repo_root / "01-tutorials"
    browser_tool_path = tutorials_path / "05-AgentCore-tools" / "02-Agent-Core-browser-tool"
    
    # Check if the paths exist
    if not tutorials_path.exists():
        raise ImportError(f"Tutorials directory not found: {tutorials_path}")
        
    if not browser_tool_path.exists():
        raise ImportError(f"Browser tool directory not found: {browser_tool_path}")
    
    # Add to sys.path if not already there
    if str(tutorials_path) not in sys.path:
        sys.path.append(str(tutorials_path))
    
    if str(browser_tool_path) not in sys.path:
        sys.path.append(str(browser_tool_path))
    
    return {
        "tutorials_path": str(tutorials_path),
        "browser_tool_path": str(browser_tool_path)
    }