# server.py
import argparse
from fastmcp import FastMCP
from github_report import load_summary

# Global config
CONFIG = {}

parser = argparse.ArgumentParser(description="GitHub Security Posture MCP")
parser.add_argument("--token", required=True, help="GitHub personal access token")
parser.add_argument("--org", default="", help="GitHub organization name (blank for user account)")
args = parser.parse_args()
CONFIG["token"] = args.token
CONFIG["org"] = args.org

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

@mcp.tool
def github_security_posture(use_cache: bool = True) -> dict:
    """
    Fetch GitHub security posture.
    Uses token/org from startup args.
    """
    return load_summary(token=CONFIG["token"], org=CONFIG["org"] or None, use_cache=use_cache)

if __name__ == "__main__":
    mcp.run()
