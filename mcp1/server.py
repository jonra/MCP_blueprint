#!/usr/bin/env python3
from fastmcp import FastMCP

mcp = FastMCP("Demo MCP")

@mcp.tool
def add_numbers(a: float, b: float) -> dict:
    """Add two numbers together."""
    return {"result": a + b}

@mcp.tool
def get_info() -> dict:
    """Get MCP demo information."""
    return {
        "concept": "MCP lets Claude call Python functions",
        "example": "Claude calls add_numbers(5, 3) → Python returns {'result': 8}"
    }

if __name__ == "__main__":
    mcp.run()