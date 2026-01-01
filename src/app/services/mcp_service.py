from typing import List, Any

from fastmcp import Client as FastMCPClient
from fastmcp.client import client
from mcp import types as mcp_types

from src.app.cmd.mcp import bell_state


class MCPService:
    server_addr: str
    mock: bool

    def __init__(
        self, server_addr: str = "http://mcp-server:8080/sse", mock: bool = False
    ) -> None:
        self.server_addr = server_addr
        self.mock = mock

    async def get_available_tools(self) -> List[mcp_types.Tool]:
        if self.mock:
            return [bell_state.to_mcp_tool()]
        async with FastMCPClient(self.server_addr) as fastmcp_client:
            return await fastmcp_client.list_tools()

    async def call_tool(self, name: str, args: dict[str, Any]) -> client.CallToolResult:
        if self.mock:
            return client.CallToolResult(
                data=bell_state.fn(),
                is_error=False,
                content=[],
                structured_content={},
                meta={},
            )
        async with FastMCPClient(self.server_addr) as fastmcp_client:
            return await fastmcp_client.call_tool(name=name, arguments=args)
