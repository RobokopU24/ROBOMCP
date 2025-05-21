from agents import Agent, Runner, set_default_openai_key, ModelSettings
from agents.mcp import MCPServer
import asyncio
import shutil
import os
import pprint
from robokop_mcp_tools import *
from robokop_mcp_server import *

from dotenv import load_dotenv
load_dotenv()
set_default_openai_key(os.getenv('OPENAI_API_KEY'))



# ----------- Agent -----------
async def run(mcp_server: MCPServer):
    print("Starting Agent ")
    agent = Agent(
        name="Assistant",
        instructions=f"Answer questions about sciences using my provided endpoints",
        mcp_servers= [mcp_server],
        model_settings=ModelSettings(tool_choice="auto"),
        tools=[get_current_edges,
               get_current_nodes,
               get_edge_summary,
               get_normalized_curie],
        # handoffs=[output_agent, edge_agent, node_agent, norm_agent],
    )

    print("here we go")
    while True:
        message = input("Enter a query or (exit to quit): ")
        if message.lower() == "exit":
            print("Goodbye!")
            break
        print("\n" + "-" * 40)
        print(f"Running: {message}")
        result = await Runner.run(starting_agent=agent, input=message)
        print(result.final_output)

    # message = "Tell me more about the node MONDO:0005148"
    # print("\n" + "-" * 40)
    # print(f"Running: {message}")
    # result = await Runner.run(starting_agent=agent, input=message)
    # pprint.pprint(result.final_output)

async def main():
    async with await get_mcp_server() as server:
        with await traced_mcp_server():
            await run(server)

if __name__ == "__main__":
    if not shutil.which("uvx"):
        raise RuntimeError("uvx is not installed. Please install it with `pip install uvx`.")
    asyncio.run(main())


    # What drugs treats MONDO:0005148?
    # Tell me more about the node MONDO:0005148
    # How many diseases is ABCA1 related to. List those diseases ?
    # What is the curie id for Alzheimer Disease?
    # What are the various kinds of edges connected to CHEBI:135285?
    # https://github.com/openai/openai-agents-python/tree/main