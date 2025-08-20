"""
Utility modules for the Competitive Intelligence Agent.
"""
from .s3_datasource import UnifiedS3DataSource
from .imports import setup_interactive_tools_import

# Configure paths on import
setup_interactive_tools_import()

__all__ = ['UnifiedS3DataSource', 'setup_interactive_tools_import']