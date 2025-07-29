#!/usr/bin/env python3
"""
MCP Server using streamable HTTP for Claude Desktop
"""
import os
import sys
from fastmcp import FastMCP

mcp = FastMCP("HTTP Demo MCP")

@mcp.tool
def add_numbers(a: float, b: float) -> dict:
    """Add two numbers together."""
    return {"result": a + b, "operation": f"{a} + {b} = {a + b}"}

@mcp.tool
def get_info() -> dict:
    """Get MCP demo information."""
    return {
        "server_name": "HTTP Demo MCP",
        "transport": "Streamable HTTP (JSON-RPC 2.0)",
        "note": "Modern MCP HTTP transport"
    }

if __name__ == "__main__":
    print("🔧 Starting HTTP MCP server...", file=sys.stderr)
    port = int(os.getenv("PORT", 8000))
    mcp.run(
        transport="streamable-http",
        host="0.0.0.0",
        port=port,
        log_level="INFO"
    )
