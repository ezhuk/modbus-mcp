import asyncio

from .server import mcp

def main() -> None:
    asyncio.run(mcp.run_async(transport="streamable-http"))
