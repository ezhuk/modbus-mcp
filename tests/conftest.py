"""Test Fixtures."""

import asyncio
import pytest
import threading

from pydantic import BaseModel
from pymodbus.datastore import (
    ModbusSequentialDataBlock,
    ModbusServerContext,
    ModbusSlaveContext,
)
from pymodbus.server import StartAsyncTcpServer

from modbus_mcp.server import ModbusMCP


class Config(BaseModel):
    host: str = "127.0.0.1"
    port: int = 5020


async def _server_main(config: Config) -> None:
    count = 100
    store = ModbusSlaveContext(
        di=ModbusSequentialDataBlock(0, [x % 2 == 1 for x in range(count)]),
        co=ModbusSequentialDataBlock(0, [x % 2 == 0 for x in range(count)]),
        hr=ModbusSequentialDataBlock(0, list(range(0, count))),
        ir=ModbusSequentialDataBlock(0, list(range(0, count))),
    )
    context = ModbusServerContext(slaves=store, single=True)
    await StartAsyncTcpServer(context, address=(config.host, config.port))


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
