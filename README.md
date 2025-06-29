## Modbus MCP Server

A lightweight [Model Context Protocol (MCP)](https://modelcontextprotocol.io) server that connects LLM agents to [Modbus](https://en.wikipedia.org/wiki/Modbus) devices in a secure, standardized way, enabling seamless integration of AI-driven workflows with Building Automation (BAS) and Industrial Control (ICS) systems, allowing agents to monitor real-time sensor data, actuate devices, and orchestrate complex automation tasks.

[![test](https://github.com/ezhuk/modbus-mcp/actions/workflows/test.yml/badge.svg)](https://github.com/ezhuk/modbus-mcp/actions/workflows/test.yml)
[![PyPI - Version](https://img.shields.io/pypi/v/modbus-mcp.svg)](https://pypi.org/p/modbus-mcp)

## Getting Started

Use [uv](https://github.com/astral-sh/uv) to add and manage the Modbus MCP server as a dependency in your project, or install it directly via `uv pip install` or `pip install`. See the [Installation](https://github.com/ezhuk/modbus-mcp/blob/main/docs/modbus-mcp/installation.mdx) section of the documentation for full installation instructions and more details.

```bash
uv add modbus-mcp
```

The server can be embedded in and run directly from your application. By default, it exposes a `Streamable HTTP` endpoint at `http://127.0.0.1:8000/mcp/`.

```python
# app.py
from modbus_mcp import ModbusMCP

mcp = ModbusMCP()

if __name__ == "__main__":
    mcp.run(transport="http")
```

It can also be launched from the command line using the provided `CLI` without modifying the source code.

```bash
modbus-mcp
```

Or in an ephemeral, isolated environment using `uvx`. Check out the [Using tools](https://docs.astral.sh/uv/guides/tools/) guide for more details.

```bash
uvx modbus-mcp
```

### Configuration

For the use cases where most operations target a specific device, such as a Programmable Logic Controller (PLC) or Modbus gateway, its connection settings (`host`, `port`, and `unit`) can be specified at runtime using environment variables so that all prompts that omit explicit connection parameters will be routed to this device.

```bash
export MODBUS_MCP_MODBUS__HOST=10.0.0.1
export MODBUS_MCP_MODBUS__PORT=502
export MODBUS_MCP_MODBUS__UNIT=1
```

These settings can also be specified in a `.env` file in the working directory.

```text
# .env
modbus__host=10.0.0.1
modbus__port=502
modbus__unit=1
```

### MCP Inspector

To confirm the server is up and running and explore available resources and tools, run the [MCP Inspector](https://modelcontextprotocol.io/docs/tools/inspector) and connect it to the Modbus MCP server at `http://127.0.0.1:8000/mcp/`. Make sure to set the transport to `Streamable HTTP`.

```bash
npx @modelcontextprotocol/inspector
```

![s01](https://github.com/user-attachments/assets/e3673921-0396-4561-8640-884e9cef609a)


## Core Concepts

The Modbus MCP server is built with [FastMCP 2.0](https://github.com/jlowin/fastmcp) and leverages its core building blocks - resource templates, tools, and prompts - to streamline Modbus read and write operations with minimal boilerplate and a clean, Pythonic interface.

### Read Registers

Each register on a device is mapped to a resource (and exposed as a tool) and [resource templates](https://gofastmcp.com/servers/resources#resource-templates) are used to specify connection details (host, port, unit) and read parameters (address, count).

```python
@mcp.resource("tcp://{host}:{port}/{address}?count={count}&unit={unit}")
@mcp.tool(
    annotations={"title": "Read Registers", "readOnlyHint": True, "openWorldHint": True}
)
async def read_registers(
    host: str = settings.modbus.host,
    port: int = settings.modbus.port,
    address: int = 40001,
    count: int = 1,
    unit: int = settings.modbus.unit,
) -> int | list[int]:
    """Reads the contents of one or more registers on a remote unit."""
    ...
```

### Write Registers

Write operations are exposed as a [tool](https://gofastmcp.com/servers/tools), accepting the same connection details (host, port, unit) and allowing to set the contents of one or more `holding registers` or `coils` in a single, atomic call.

```python
@mcp.tool(
    annotations={
        "title": "Write Registers",
        "readOnlyHint": False,
        "openWorldHint": True,
    }
)
async def write_registers(
    data: list[int],
    host: str = settings.modbus.host,
    port: int = settings.modbus.port,
    address: int = 40001,
    unit: int = settings.modbus.unit,
) -> str:
    """Writes data to one or more registers on a remote unit."""
    ...
```

### Authentication

To enable Bearer Token authentication for the `Streamable HTTP` transport, provide the RSA public key in PEM format in the `.env` file. Check out the [Bearer Token Authentication](https://gofastmcp.com/servers/auth/bearer) section for more details.

### Interactive Prompts

Structured response messages are implemented using [prompts](https://gofastmcp.com/servers/prompts) that help guide the interaction, clarify missing parameters, and handle errors gracefully.

```python
@mcp.prompt(name="modbus_help", tags={"modbus", "help"})
def modbus_help() -> list[Message]:
    """Provides examples of how to use the Modbus MCP server."""
    ...
```

Here are some example text inputs that can be used to interact with the server.

```text
Please read the value of register 40001 on 127.0.0.1:502.
Set register 40005 to 123 on host 192.168.1.10, unit 3.
Write [1, 2, 3] to holding registers starting at address 40010.
What is the status of input register 30010 on 10.0.0.5?
```

## Examples

The `examples` folder contains sample projects showing how to integrate with the Modbus MCP server using various client APIs to provide tools and context to LLMs.

- [openai-agents](https://github.com/ezhuk/modbus-mcp/tree/main/examples/openai-agents) - shows how to connect to the Modbus MCP server using the [OpenAI Agents SDK](https://openai.github.io/openai-agents-python/mcp/).
- [openai](https://github.com/ezhuk/modbus-mcp/tree/main/examples/openai) - a minimal app leveraging remote MCP server support in the [OpenAI Python library](https://platform.openai.com/docs/guides/tools-remote-mcp).
- [pydantic-ai](https://github.com/ezhuk/modbus-mcp/tree/main/examples/pydantic-ai) - shows how to connect to the Modbus MCP server using the [PydanticAI Agent Framework](https://ai.pydantic.dev).

## Docker

The Modbus MCP server can be deployed as a Docker container as follows:

```bash
docker run -d \
  --name modbus-mcp \
  --restart=always \
  -p 8080:8000 \
  --env-file .env \
  ghcr.io/ezhuk/modbus-mcp:latest
```

This maps port `8080` on the host to the MCP server's port `8000` inside the container and loads settings from the `.env` file, if present.

## License

The server is licensed under the [MIT License](https://github.com/ezhuk/modbus-mcp?tab=MIT-1-ov-file).
