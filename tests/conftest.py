"""Test Fixtures."""

import asyncio
import pytest
import threading

from pymodbus.datastore import (
    ModbusSequentialDataBlock,
    ModbusServerContext,
    ModbusSlaveContext,
)
from pymodbus.server import StartAsyncTcpServer


async def server_main() -> None:
    count = 100
    store = ModbusSlaveContext(
        di=ModbusSequentialDataBlock(0, [x % 2 == 1 for x in range(count)]),
        co=ModbusSequentialDataBlock(0, [x % 2 == 0 for x in range(count)]),
        hr=ModbusSequentialDataBlock(0, list(range(0, count))),
        ir=ModbusSequentialDataBlock(0, list(range(0, count))),
    )
    context = ModbusServerContext(slaves=store, single=True)
    await StartAsyncTcpServer(context, address=("127.0.0.1", 5020))


def thread_main():
    asyncio.run(server_main())


@pytest.fixture(scope="session")
def modbus_server():
    thread = threading.Thread(target=thread_main, daemon=True)
    thread.start()
    yield
