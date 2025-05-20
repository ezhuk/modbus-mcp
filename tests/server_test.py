"""Server tests."""

import pytest

from fastmcp import Client
from pydantic import AnyUrl

import modbus_mcp.server as server_module
from modbus_mcp.server import mcp

@pytest.fixture(autouse=True)
def patch_modbus_client(monkeypatch):
    """Patch AsyncModbusTcpClient."""
    class MockResponse:
        """Mock Modbus response."""
        def __init__(self, registers=None, bits=None, error=False):
            self.registers = registers
            self.bits = bits
            self._error = error
        def isError(self):
            return self._error

    class MockClient:
        """Mock Modbus client."""
        def __init__(self, host, port):
            self.host = host
            self.port = port

        async def connect(self):
            return True

        def close(self):
            pass

        async def read_coils(self, addr, count, slave):
            return MockResponse(bits=[((addr + i) % 2 == 0) for i in range(count)])

        async def read_holding_registers(self, addr, count, slave):
            return MockResponse(registers=[addr + i for i in range(count)])

        async def read_input_registers(self, addr, count, slave):
            return MockResponse(registers=[addr + i for i in range(count)])

        async def write_registers(self, addr, values, slave):
            return MockResponse(error=False)

    monkeypatch.setattr(server_module, "AsyncModbusTcpClient", MockClient)
    return []

@pytest.mark.anyio
async def test_read_registers(patch_modbus_client):
    """Test read_registers resource."""
    async with Client(mcp) as client:
        result = await client.read_resource(
            AnyUrl("tcp://127.0.0.1:502/40010?count=1&unit=1")
        )
        assert len(result) == 1
        assert result[0].text == '9'

@pytest.mark.anyio
async def test_write_registers(patch_modbus_client):
    """Test write_registers tool."""
    async with Client(mcp) as client:
        result = await client.call_tool(
            "write_registers", {
                "host": "127.0.0.1",
                "port": 502,
                "address": 40001,
                "data": [565],
                "unit": 1
            }
        )
        assert len(result) == 1
        assert "succedeed" in result[0].text

@pytest.mark.anyio
async def test_help_prompt():
    async with Client(mcp) as client:
        result = await client.get_prompt("modbus_help", {})
        assert len(result.messages) == 5

@pytest.mark.anyio
async def test_error_prompt():
    async with Client(mcp) as client:
        result = await client.get_prompt("modbus_error", {
            "error": "Could not read data"
        })
        assert len(result.messages) == 2
