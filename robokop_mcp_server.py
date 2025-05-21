from agents.mcp import MCPServerStdio
from agents import trace
import yaml

with open("config.yaml") as f:
    config = yaml.safe_load(f).get("robokopServertool")


async def get_mcp_server():
    """Creates and returns an MCPServerStdio instance wrapped in a trace context."""
    return MCPServerStdio(
        cache_tools_list=True,
        params=config,
        client_session_timeout_seconds=300
    )

async def traced_mcp_server():
    """Context manager for MCPServer with trace."""
    return trace(workflow_name="MCP ROBOKOP Trace")
