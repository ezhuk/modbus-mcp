from fastmcp import FastMCP
from fastmcp.server.auth.providers.workos import AuthKitProvider
from fastmcp.prompts.prompt import Message
from fastmcp.resources import ResourceTemplate
from pymodbus.client import AsyncModbusTcpClient

from modbus_mcp.settings import Settings
from modbus_mcp.utils import get_device


settings = Settings()

_READ_FN = {
    0: ("read_coils", 1),
    1: ("read_discrete_inputs", 10001),
    3: ("read_input_registers", 30001),
    4: ("read_holding_registers", 40001),
}

_WRITE_FN = {0: ("write_coils", 1), 4: ("write_registers", 40001)}


async def read_registers(
    address: int = 40001,
    count: int = 1,
    name: str | None = None,
    host: str | None = None,
    port: int | None = None,
    unit: int | None = None,
) -> int | list[int]:
    """Reads the contents of one or more registers on a remote unit."""
    try:
        host, port, unit = get_device(settings, name, host, port, unit)
        async with AsyncModbusTcpClient(host, port=port) as client:
            func, offset = _READ_FN[address // 10000]
            method = getattr(client, func)
            res = await method(address - offset, count=count, device_id=unit)
            out = getattr(res, "registers", []) or getattr(res, "bits", [])
            return [int(x) for x in out] if count > 1 else out[0]
    except Exception as e:
        raise RuntimeError(
            f"Could not read {address} ({count}) from {host}:{port}"
        ) from e


async def write_registers(
    data: list[int],
    address: int = 40001,
    name: str | None = None,
    host: str | None = None,
    port: int | None = None,
    unit: int | None = None,
) -> str:
    """Writes data to one or more registers on a remote unit."""
    try:
        host, port, unit = get_device(settings, name, host, port, unit)
        async with AsyncModbusTcpClient(host, port=port) as client:
            func, offset = _WRITE_FN[address // 10000]
            method = getattr(client, func)
            res = await method(address - offset, data, device_id=unit)
            if res.isError():
                raise RuntimeError(f"Could not write to {address} on {host}:{port}")
            return f"Write to {address} on {host}:{port} has succedeed"
    except Exception as e:
        raise RuntimeError(f"{e}") from e


async def mask_write_register(
    address: int = 40001,
    and_mask: int = 0xFFFF,
    or_mask: int = 0x0000,
    name: str | None = None,
    host: str | None = None,
    port: int | None = None,
    unit: int | None = None,
) -> str:
    """Mask writes data to a specified register."""
    try:
        host, port, unit = get_device(settings, name, host, port, unit)
        async with AsyncModbusTcpClient(host, port=port) as client:
            res = await client.mask_write_register(
                address=(address - 40001),
                and_mask=and_mask,
                or_mask=or_mask,
                device_id=unit,
            )
            if res.isError():
                raise RuntimeError(
                    f"Could not mask write to {address} on {host}:{port}"
                )
            return f"Mask write to {address} on {host}:{port} has succedeed"
    except Exception as e:
        raise RuntimeError(f"{e}") from e


async def search(query: str) -> list[int]:
    """Deep Research search registers."""
    offset, sep, count = query.strip().partition(",")
    start = int(offset)
    res = []
    for x in range(int(count) if sep else 100):
        try:
            addr = start + x
            await read_registers(address=addr)
            res.append(addr)
        except Exception:
            continue
    return res


async def fetch(id: str) -> int | list[int]:
    """Deep Research fetch the contents of one or more registers."""
    addr, sep, count = id.strip().partition(",")
    return await read_registers(address=int(addr), count=int(count) if sep else 1)


def modbus_help() -> list[Message]:
    """Provides examples of how to use the Modbus MCP server."""
    return [
        Message("Here are examples of how to read and write registers:"),
        Message("Please read the value of register 40001 on 127.0.0.1:502."),
        Message("Set register 40005 to 123 on host 192.168.1.10, unit 3."),
        Message("Write [1, 2, 3] to holding registers starting at address 40010."),
        Message("What is the status of input register 30010 on 10.0.0.5?"),
    ]


def modbus_error(error: str | None = None) -> list[Message]:
    """Asks the user how to handle an error."""
    return (
        [
            Message(f"ERROR: {error!r}"),
            Message("Would you like to retry, change parameters, or abort?"),
        ]
        if error
        else []
    )


class ModbusMCP(FastMCP):
    def __init__(self, **kwargs):
        super().__init__(
            name="Modbus MCP Server",
            auth=(
                AuthKitProvider(
                    authkit_domain=settings.auth.domain, base_url=settings.auth.url
                )
                if settings.auth.domain and settings.auth.url
                else None
            ),
            **kwargs,
        )

        self.add_template(
            ResourceTemplate.from_function(
                fn=read_registers,
                uri_template="tcp://{host}:{port}/{address}{?count,unit}",
            )
        )

        self.tool(
            read_registers,
            annotations={
                "title": "Read Registers",
                "readOnlyHint": True,
                "openWorldHint": True,
            },
        )

        self.tool(
            write_registers,
            annotations={
                "title": "Write Registers",
                "readOnlyHint": False,
                "openWorldHint": True,
            },
        )

        self.tool(
            mask_write_register,
            annotations={
                "title": "Mask Write Register",
                "readOnlyHint": False,
                "openWorldHint": True,
            },
        )

        self.tool(
            search,
            annotations={
                "title": "Search",
                "readOnlyHint": True,
                "openWorldHint": True,
            },
        )

        self.tool(
            fetch,
            annotations={
                "title": "Fetch",
                "readOnlyHint": True,
                "openWorldHint": True,
            },
        )

        self.prompt(modbus_error, name="modbus_error", tags={"modbus", "error"})
        self.prompt(modbus_help, name="modbus_help", tags={"modbus", "help"})
