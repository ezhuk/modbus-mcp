import asyncio
from contextlib import asynccontextmanager
from dataclasses import dataclass

from fastmcp import FastMCP, Context
from fastmcp.prompts.prompt import Message
from pymodbus.client import AsyncModbusTcpClient

@dataclass
class AppContext:
    client: AsyncModbusTcpClient

@asynccontextmanager
async def lifespan(server: FastMCP):
    client = AsyncModbusTcpClient("127.0.0.1")
    await client.connect()
    try:
        yield AppContext(client=client)
    except Exception as e:
        print(f"ERROR: {e}")
    finally:
        if client.connected:
            await client.close()

mcp = FastMCP(
    name="Modbus MCP Server",
    lifespan=lifespan
)

@mcp.resource("modbus://{unit}/{type}/{address}")
async def read_one(
    ctx: Context,
    unit: int,
    type: str,
    address: int
) -> int | bool:
    client: AsyncModbusTcpClient = ctx.request_context.lifespan_context.client
    if type == "holding":
        r = await client.read_holding_registers(address, count=1, unit=unit)
        return r.registers[0]
    elif type == "input":
        r = await client.read_input_registers(address, count=1, unit=unit)
        return r.registers[0]
    elif type == "coil":
        r = await client.read_coils(address, count=1, unit=unit)
        return r.bits[0]
    elif type == "discrete":
        r = await client.read_discrete_inputs(address, count=1, unit=unit)
        return r.bits[0]
    else:
        raise RuntimeError(f"Unsupported register type: '{type}'")

@mcp.resource("modbus://{unit}/{type}?start={start}&count={count}")
async def read_many(
    ctx: Context,
    unit: int,
    type: str,
    start: int,
    count: int
) -> list[int | bool]:
    client: AsyncModbusTcpClient = ctx.request_context.lifespan_context.client
    if type == "holding":
        r = await client.read_holding_registers(start, count=count, unit=unit)
        return r.registers
    elif type == "input":
        r = await client.read_input_registers(start, count=count, unit=unit)
        return r.registers
    elif type == "coil":
        r = await client.read_coils(start, count=count, unit=unit)
        return r.bits
    elif type == "discrete":
        r = await client.read_discrete_inputs(start, count=count, unit=unit)
        return r.bits
    else:
        raise RuntimeError(f"Unsupported register type: '{type}'")

@mcp.tool()
async def write_one(
    ctx: Context,
    unit: int,
    type: str,
    address: int,
    value: int | bool
) -> None:
    client: AsyncModbusTcpClient = ctx.request_context.lifespan_context.client
    if type in ("holding", "input"):
        await client.write_register(address, value, unit=unit)
    elif type == "coil":
        await client.write_coil(address, value, unit=unit)
    else:
        raise RuntimeError(f"Type '{type}' does not support single-write")

@mcp.tool()
async def write_many(
    ctx: Context,
    unit: int,
    type: str,
    start: int,
    values: list[int | bool]
) -> None:
    client: AsyncModbusTcpClient = ctx.request_context.lifespan_context.client
    if type in ("holding", "input"):
        await client.write_registers(start, values, unit=unit)
    elif type == "coil":
        await client.write_coils(start, values, unit=unit)
    else:
        raise RuntimeError(f"Type '{type}' does not support multi-write")

@mcp.prompt(
    name="clarify_modbus_read",
    description="Ask the user to specify missing Modbus read parameters",
    tags={"modbus", "read"}
)

def clarify_modbus_read(
    unit: int | None = None,
    type: str | None = None,
    address: int | None = None,
    start: int | None = None,
    count: int | None = None
) -> list[Message]:
    prompts: list[Message] = []
    if unit is None:
        prompts.append(Message("Please specify the Modbus unit ID you want to read from."))
    if type is None:
        prompts.append(Message("Which register type do you want to read from? Choose from 'holding', 'input', 'coil', or 'discrete'."))
    if address is None and (start is None or count is None):
        prompts.append(
            Message(
                "To read a single register/coil, provide `address`."
                "To read multiple, provide both `start` and `count`."
            )
        )
    return prompts

@mcp.prompt(
    name="clarify_modbus_write",
    description="Ask the user to specify missing Modbus write parameters",
    tags={"modbus", "write"}
)
def clarify_modbus_write(
    unit: int | None = None,
    type: str | None = None,
    address: int | None = None,
    start: int | None = None,
    values: list[int | bool] | None = None
) -> list[Message]:
    prompts: list[Message] = []
    if unit is None:
        prompts.append(Message("Please specify the Modbus unit ID you want to write to."))
    if type is None:
        prompts.append(Message("Which register type do you want to write? 'holding' or 'coil'."))
    if address is None and start is None:
        prompts.append(Message("For a single write, provide `address` and `value`. For a bulk write, provide `start` and `values` list."))
    if values is None:
        prompts.append(Message("Please provide the value (or list of values) you wish to write."))
    return prompts

