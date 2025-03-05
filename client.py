import asyncio
from dataclasses import dataclass
from typing import Optional
from contextlib import AsyncExitStack

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()  # load environment variables from .env

@dataclass
class AIMessage:
    role: str
    content: str


class MCPClient:
    def __init__(self):
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()
        self.anthropic = Anthropic()

    async def connect_to_server(self, server_script_path: str):
        """Connect to an MCP server

        Args:
            server_script_path: Path to the server script (.py or .js)
        """
        is_python = server_script_path.endswith('.py')
        is_js = server_script_path.endswith('.js')
        if not (is_python or is_js):
            raise ValueError("Server script must be a .py or .js file")

        command = "python" if is_python else "node"
        server_params = StdioServerParameters(
            command=command,
            args=[server_script_path],
            env=None
        )

        stdio_transport = await self.exit_stack.enter_async_context(stdio_client(server_params))
        self.stdio, self.write = stdio_transport
        self.session = await self.exit_stack.enter_async_context(ClientSession(self.stdio, self.write))

        await self.session.initialize()

        # List available tools
        response = await self.session.list_tools()
        tools = response.tools
        print("\nConnected to server with tools:", [tool.name for tool in tools])

    async def process_query(self, query: str) -> str:
        """Process a query using Claude and available tools with preserved context for agentic behavior"""
        messages = []
        messages.append({
            "role": "user",
            "content": "Please respond with a full list of actions you plan to take based on what I ask. I would like to see the steps you intend to take, and any tools you plan to call."
        })
        messages.append(
            {
                "role": "user",
                "content": query
            })


        response = await self.session.list_tools()
        available_tools = [{
            "name": tool.name,
            "description": tool.description,
            "input_schema": tool.inputSchema
        } for tool in response.tools]

        tool_results = []
        final_text = []

        while True:
            # Send a request to the LLM with available tools and current conversation context
            response = self.anthropic.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1000,
                messages=messages,
                tools=available_tools
            )

            # Handle response from the LLM
            for content in response.content:
                if content.type == 'text':
                    # final_text.append(content.text)
                    print("<------------------>")
                    print(content.text)
                    print("<------------------>")
                    messages.append({
                        "role": "assistant",
                        "content": content.text
                    })

                elif content.type == 'tool_use':
                    tool_name = content.name
                    tool_args = content.input

                    # Execute the tool call and store the result
                    result = await self.session.call_tool(tool_name, tool_args)
                    tool_results.append({"call": tool_name, "result": result})

                    # Add tool call and result to messages
                    messages.append({
                        "role": "assistant",
                        "content": [
                            {
                            "type": "tool_use",
                            "id": content.id,
                            "name": content.name,
                            "input": content.input
                            }
                        ]
                    })

                    # messages.append(content)

                    messages.append({
                        "role": "user",
                        "content": [{
                            "type": "tool_result",
                            "tool_use_id": content.id,
                            "content": result.content[0].text
                        }]

                    })

                    # Break, reevaluate, and continue the loop with updated context
                    break
            else:
                # If no tool-use content exists, we assume final response; break the loop
                break

        return "\n".join(final_text)

    async def chat_loop(self):
        """Run an interactive chat loop"""
        print("\nDoes a set of all sets contain itself?")
        print("Type your queries or 'quit' to exit.")

        while True:
            try:
                query = input("\nQuery: ").strip()

                if query.lower() == 'quit':
                    break

                response = await self.process_query(query)
                print("\n" + response)

            except Exception as e:
                print(f"\nError: {str(e)}")

    async def cleanup(self):
        """Clean up resources"""
        await self.exit_stack.aclose()

async def main():
    if len(sys.argv) < 2:
        print("Usage: python client.py <path_to_server_script>")
        sys.exit(1)

    client = MCPClient()
    try:
        await client.connect_to_server(sys.argv[1])
        await client.chat_loop()
    finally:
        await client.cleanup()

if __name__ == "__main__":
    import sys
    asyncio.run(main())