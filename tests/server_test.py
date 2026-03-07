import pytest

from fastmcp.exceptions import McpError, ToolError
from pydantic import AnyUrl
from starlette.requests import Request


@pytest.mark.asyncio
async def test_read_registers(server, mcp, client):
    """Test read_registers resource."""
    result = await client.read_resource(
        AnyUrl(f"tcp://{server.host}:{server.port}/40010?count=1&unit=1")
    )
    assert len(result) == 1
    assert result[0].text == "10"

    with pytest.raises(McpError) as e:
        await client.read_resource(AnyUrl("tcp://none:502/40010?count=1&unit=1"))
    assert "Could not read" in str(e.value)


@pytest.mark.asyncio
async def test_write_registers(server, mcp, client):
    """Test write_registers tool."""
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
    assert len(result.content) == 1
    assert "succedeed" in result.content[0].text

    with pytest.raises(ToolError) as e:
        await client.call_tool(
            "write_registers",
            {
                "host": "none",
                "port": 502,
                "address": 40001,
                "data": [565],
                "unit": 1,
            },
        )
    assert "Error calling tool" in str(e.value)


@pytest.mark.asyncio
async def test_mask_write_register(server, mcp, client):
    """Test mask_write_register tool."""
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
    assert len(result.content) == 1
    assert "succedeed" in result.content[0].text

    with pytest.raises(ToolError) as e:
        await client.call_tool(
            "mask_write_register",
            {
                "host": "none",
                "port": 502,
                "address": 40001,
                "and_mask": 0xFFFF,
                "or_mask": 0x0000,
                "unit": 1,
            },
        )
    assert "Error calling tool" in str(e.value)


@pytest.mark.asyncio
async def test_help_prompt(mcp, client):
    """Test help prompt."""
    result = await client.get_prompt("modbus_help", {})
    assert len(result.messages) == 5


@pytest.mark.asyncio
async def test_error_prompt(mcp, client):
    """Test error prompt."""
    result = await client.get_prompt("modbus_error", {"error": "Could not read data"})
    assert len(result.messages) == 2

    result = await client.get_prompt("modbus_error", {"error": ""})
    assert len(result.messages) == 0


@pytest.mark.asyncio
async def test_health_check(mcp):
    response = await mcp.health_check(
        Request(
            {
                "type": "http",
                "method": "GET",
                "path": "/health",
                "headers": [],
            }
        )
    )
    assert response.status_code == 200
