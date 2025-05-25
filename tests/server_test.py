"""Server tests."""

import pytest

from fastmcp import Client
from pydantic import AnyUrl

from modbus_mcp.server import mcp


@pytest.mark.asyncio
async def test_read_registers(modbus_server):
    """Test read_registers resource."""
    async with Client(mcp) as client:
        result = await client.read_resource(
            AnyUrl("tcp://127.0.0.1:5020/40010?count=1&unit=1")
        )
        assert len(result) == 1
        assert result[0].text == "10"


@pytest.mark.asyncio
async def test_write_registers(modbus_server):
    """Test write_registers tool."""
    async with Client(mcp) as client:
        result = await client.call_tool(
            "write_registers",
            {
                "host": "127.0.0.1",
                "port": 5020,
                "address": 40001,
                "data": [565],
                "unit": 1,
            },
        )
        assert len(result) == 1
        assert "succedeed" in result[0].text


@pytest.mark.asyncio
async def test_mask_write_registers(modbus_server):
    """Test mask_write_registers tool."""
    async with Client(mcp) as client:
        result = await client.call_tool(
            "mask_write_register",
            {
                "host": "127.0.0.1",
                "port": 5020,
                "address": 40001,
                "and_mask": 0xFFFF,
                "or_mask": 0x0000,
                "unit": 1,
            },
        )
        assert len(result) == 1
        assert "succedeed" in result[0].text


@pytest.mark.asyncio
async def test_help_prompt():
    """Test help prompt."""
    async with Client(mcp) as client:
        result = await client.get_prompt("modbus_help", {})
        assert len(result.messages) == 5


@pytest.mark.asyncio
async def test_error_prompt():
    """Test error prompt."""
    async with Client(mcp) as client:
        result = await client.get_prompt(
            "modbus_error", {"error": "Could not read data"}
        )
        assert len(result.messages) == 2
