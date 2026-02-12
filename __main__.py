"""
Bolor Brain MCP Server - Main Entry Point
==========================================

Run the MCP server as a module:
    python -m bolor-brain-mcp

Or after installation:
    bolor-brain-mcp
"""

from mcp_server import main
import asyncio

if __name__ == "__main__":
    asyncio.run(main())
