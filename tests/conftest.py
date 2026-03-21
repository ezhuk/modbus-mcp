import asyncio
import pytest
import pytest_asyncio
import threading

from fastmcp import Client

from pydantic import BaseModel
from pymodbus import ModbusDeviceIdentification
from pymodbus.datastore import (
    ModbusSequentialDataBlock,
    ModbusServerContext,
    ModbusDeviceContext,
)
from pymodbus.server import StartAsyncTcpServer

from modbus_mcp.server import ModbusMCP


class Config(BaseModel):
    host: str = "127.0.0.1"
    port: int = 5020


async def _server_main(config: Config) -> None:
    count = 100
    store = ModbusDeviceContext(
        di=ModbusSequentialDataBlock(0, [x % 2 == 1 for x in range(count)]),
        co=ModbusSequentialDataBlock(0, [x % 2 == 0 for x in range(count)]),
        hr=ModbusSequentialDataBlock(0, list(range(0, count))),
        ir=ModbusSequentialDataBlock(0, list(range(0, count))),
    )
    context = ModbusServerContext(devices=store, single=True)
    identity = ModbusDeviceIdentification()
    identity.VendorName = "Test Vendor"
    identity.VendorUrl = "example.com"
    identity.ProductCode = "Test Product Code"
    identity.ProductName = "Test Product Name"
    identity.ModelName = "Test Model"
    identity.MajorMinorRevision = "1.0"
    identity.UserApplicationName = "Test App"
    await StartAsyncTcpServer(
        context, address=(config.host, config.port), identity=identity
    )


@pytest.fixture(scope="session")
def server():
    config = Config()
    thread = threading.Thread(
        target=lambda: asyncio.run(_server_main(config)), daemon=True
    )
    thread.start()
    yield config


@pytest.fixture(scope="session")
def mcp():
    return ModbusMCP()


@pytest_asyncio.fixture
async def client(mcp):
    async with Client(mcp) as c:
        yield c


@pytest.fixture()
def cli(monkeypatch):
    async def dummy_run_async(self, transport):
        return

    monkeypatch.setattr(
        "modbus_mcp.cli.ModbusMCP.run_async",
        dummy_run_async,
    )
