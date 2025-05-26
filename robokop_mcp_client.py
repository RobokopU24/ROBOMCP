import asyncio
import json
import argparse
import ollama
from typing import Optional, Any, List, Dict
from dotenv import load_dotenv
from contextlib import AsyncExitStack

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from openai import AsyncOpenAI
load_dotenv()


class MCPBaseClient:
    def __init__(self, model: str):
        self.messages: List[Dict[str, Any]] = []
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()
        self.model = model
        self.stdio: Optional[Any] = None
        self.write: Optional[Any] = None

    async def connect_to_server(self, server_script_path: str):
        server_params = StdioServerParameters(command="python", args=[server_script_path])
        stdio_transport = await self.exit_stack.enter_async_context(stdio_client(server_params))
        self.stdio, self.write = stdio_transport
        self.session = await self.exit_stack.enter_async_context(ClientSession(self.stdio, self.write))
        await self.session.initialize()

        response = await self.session.list_tools()
        print("\nConnected to server with tools:", [tool.name for tool in response.tools])

    async def get_available_tools(self) -> List[Dict[str, Any]]:
        tool_list = await self.session.list_tools()
        return [{
            "type": "function",
            "function": {
                "name": tool.name,
                "description": tool.description,
                "parameters": tool.inputSchema
            }
        } for tool in tool_list.tools]

    async def process_query(self, query: str) -> str:
        self.messages.append({"role": "user", "content": query})
        tools = await self.get_available_tools()

        message = await self.llm_chat(self.messages, tools)
        self.messages.append(message)

        while getattr(message, "tool_calls", None):
            for tool_call in message.tool_calls:
                args = tool_call.function.arguments
                if isinstance(args, str):
                    args = json.loads(args)
                tool_result = await self.session.call_tool(tool_call.function.name, arguments=args)
                self.messages.append({
                    "role": "tool",
                    "tool_call_id": getattr(tool_call, "id", None),
                    "content": tool_result.content[0].text
                })

            message = await self.llm_chat(self.messages, tools)
            self.messages.append(message)

        return message.content

    async def llm_chat(self, messages: List[Dict[str, Any]], tools: List[Dict[str, Any]]):
        raise NotImplementedError("llm_chat must be implemented by subclasses")

    async def cleanup(self):
        await self.exit_stack.aclose()

class MCPOpenAIClient(MCPBaseClient):
    def __init__(self, model="gpt-4-turbo"):
        super().__init__(model)
        self.llm_client = AsyncOpenAI()

    async def llm_chat(self, messages, tools):
        response = await self.llm_client.chat.completions.create(
            model=self.model,
            messages=messages,
            tools=tools,
            tool_choice="auto"
        )
        return response.choices[0].message


class MCPOllamaClient(MCPBaseClient):
    def __init__(self, model="llama3.2"):
        super().__init__(model)

    async def llm_chat(self, messages, tools):
        response = ollama.chat(
            model=self.model,
            messages=messages,
            tools=tools
        )
        return response.message

async def run_client(client):
    try:
        await client.connect_to_server("robokop_mcp_server.py")
        print("\nMCP Client Started!")
        print("Type your queries or 'quit' to exit or 'reset' chat context.")
        while True:
            query = input("\nQuery: ").strip()
            if query.lower() in {'quit', 'exit', 'bye', 'q', 'x'}:
                print("\nGoodbye!")
                break
            if query.lower() == 'reset':
                client.messages.clear()
                print("\nContext reset.")
                continue
            response = await client.process_query(query)
            print(f"\nResponse: {response}")
    except Exception as e:
        print(f"\nError: {e}")
    finally:
        await client.cleanup()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--provider", choices=["openai", "ollama"], default="ollama", help="Choose the LLM provider")
    args = parser.parse_args()

    client = MCPOpenAIClient() if args.provider == "openai" else MCPOllamaClient()
    asyncio.run(run_client(client))









# ----------- Sample queries -----------

    # What drugs treats MONDO:0005148?
    # Tell me more about the node MONDO:0005148
    # Tell me more about MONDO:0004979
    # How many diseases is ABCA1 related to. List those diseases ?
    # What is the curie id for Alzheimer Disease?
    # What are the various kinds of edges connected to CHEBI:135285?
    # https://modelcontextprotocol.io/quickstart/server