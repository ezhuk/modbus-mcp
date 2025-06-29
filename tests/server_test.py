"""Server tests."""

import pytest

from fastmcp import Client
from pydantic import AnyUrl


@pytest.mark.asyncio
async def test_read_registers(server, mcp):
    """Test read_registers resource."""
    async with Client(mcp) as client:
        result = await client.read_resource(
            AnyUrl(f"tcp://{server.host}:{server.port}/40010?count=1&unit=1")
        )
        assert len(result) == 1
        assert result[0].text == "10"


@pytest.mark.asyncio
async def test_write_registers(server, mcp):
    """Test write_registers tool."""
    async with Client(mcp) as client:
        result = await client.call_tool(
            "write_registers",
            {
                "host": server.host,
                "port": server.port,
                "address": 40001,
                "data": [565],
                "unit": 1,
            },
        )
        assert len(result) == 1
        assert "succedeed" in result[0].text


@pytest.mark.asyncio
async def test_mask_write_registers(server, mcp):
    """Test mask_write_registers tool."""
    async with Client(mcp) as client:
        result = await client.call_tool(
            "mask_write_register",
            {
                "host": server.host,
                "port": server.port,
                "address": 40001,
                "and_mask": 0xFFFF,
                "or_mask": 0x0000,
                "unit": 1,
            },
        )
        assert len(result) == 1
        assert "succedeed" in result[0].text


@pytest.mark.asyncio
async def test_help_prompt(mcp):
    """Test help prompt."""
    async with Client(mcp) as client:
        result = await client.get_prompt("modbus_help", {})
        assert len(result.messages) == 5


@pytest.mark.asyncio
async def test_error_prompt(mcp):
    """Test error prompt."""
    async with Client(mcp) as client:
        result = await client.get_prompt(
            "modbus_error", {"error": "Could not read data"}
        )
        assert len(result.messages) == 2
