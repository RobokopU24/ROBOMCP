import asyncio
import json
from typing import Optional, Any, List, Dict
from dotenv import load_dotenv
from contextlib import AsyncExitStack

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from openai import AsyncOpenAI
load_dotenv()


class MCPOpenAIClient:
    def __init__(self, model:str="gpt-4-turbo"):
        # Initialize session and client objects
        self.messages: List[Dict[str, Any]] = []
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()
        self.openai_client = AsyncOpenAI()
        self.model = model
        self.stdio:Optional[Any] = None
        self.write:Optional[Any] = None

    async def connect_to_server(self, server_script_path: "robokop_mcp_server.py"):
        """Connect to an MCP server

        Args:
            server_script_path: Path to the server script (.py)
        """
        # Configure server
        server_params = StdioServerParameters(
            command="python",
            args=[server_script_path],
            env=None
        )
        # Connect to server
        stdio_transport = await self.exit_stack.enter_async_context(stdio_client(server_params))
        self.stdio, self.write = stdio_transport
        self.session = await self.exit_stack.enter_async_context(ClientSession(self.stdio, self.write))

        await self.session.initialize()

        # List available tools
        response = await self.session.list_tools()
        tools = response.tools
        print("\nConnected to server with tools:", [tool.name for tool in tools])
        # methods will go here

    async def process_query( self, query: str ) -> str:
        """Process a query using LLM and available tools"""

        self.messages.append({
            "role": "user",
            "content": query
        })

        tool_list = await self.session.list_tools()
        available_tools = [{
            "type": "function",
            "function": {
                "name": tool.name,
                "description": tool.description,
                "parameters": tool.inputSchema
            }
        } for tool in tool_list.tools]

        # Initial openAI API call
        response = await self.openai_client.chat.completions.create(
            model=self.model,
            messages=self.messages,
            tools=available_tools,
            tool_choice="auto"
        )

        # Process response and handle tool calls
        message = response.choices[0].message
        self.messages.append(message)
        while message.tool_calls:
            for tool_call in message.tool_calls:
                tool_result = await self.session.call_tool(
                    tool_call.function.name,
                    arguments=json.loads(tool_call.function.arguments)
                )
                self.messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": tool_result.content[0].text
                })

            response = await self.openai_client.chat.completions.create(
                model=self.model,
                messages=self.messages,
                tools=available_tools,
                tool_choice="auto"
            )
            message = response.choices[0].message
            self.messages.append(message)

        return message.content

    async def cleanup( self ):
        """Clean up resources"""
        await self.exit_stack.aclose()


async def main():
    # Main Entry Point
    client = MCPOpenAIClient()
    try:
        await client.connect_to_server("robokop_mcp_server.py")

        print("\nMCP Client Started!")
        print("Type your queries or 'quit' to exit or 'reset' chat context.")

        while True:
            try:
                query = input("\nQuery: ").strip()

                if query.lower() in ['quit', 'end', 'exit', 'bye']:
                    print("\nGoodBye!")
                    break

                if query.lower() == 'reset':
                    client.messages=[]
                    print("\nContext reset.")
                    continue

                response = await client.process_query(query)
                print(f"\nResponse: {response}")

            except Exception as e:
                print(f"\nError: {str(e)}")

    finally:
        await client.cleanup()

if __name__ == "__main__":
    asyncio.run(main())









# ----------- Sample queries -----------

    # What drugs treats MONDO:0005148?
    # Tell me more about the node MONDO:0005148
    # Tell me more about MONDO:0004979
    # How many diseases is ABCA1 related to. List those diseases ?
    # What is the curie id for Alzheimer Disease?
    # What are the various kinds of edges connected to CHEBI:135285?
    # https://modelcontextprotocol.io/quickstart/server