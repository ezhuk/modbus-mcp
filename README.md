## Modbus MCP Server

A lightweight [Model Context Protocol (MCP)](https://modelcontextprotocol.io) server that connects LLM agents to [Modbus](https://en.wikipedia.org/wiki/Modbus) devices in a secure, standardized way, enabling seamless integration of AI-driven workflows with Building Automation (BAS) and Industrial Control (ICS) systems, allowing agents to monitor real-time sensor data, actuate devices, and orchestrate complex automation tasks.

[![test](https://github.com/ezhuk/modbus-mcp/actions/workflows/test.yml/badge.svg)](https://github.com/ezhuk/modbus-mcp/actions/workflows/test.yml)
[![PyPI - Version](https://img.shields.io/pypi/v/modbus-mcp.svg?color=blue)](https://pypi.org/p/modbus-mcp)

## Getting Started

The server is built with [FastMCP 2.0](https://gofastmcp.com/getting-started/welcome) and uses [uv](https://github.com/astral-sh/uv) for project and dependency management. Simply run the following command to install `uv` or check out the [installation guide](https://docs.astral.sh/uv/getting-started/installation/) for more details and alternative installation methods.

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Clone the repository, then use `uv` to install project dependencies and create a virtual environment.

```bash
git clone https://github.com/ezhuk/modbus-mcp.git
cd modbus-mcp
uv sync
```

Start the Modbus MCP server by running the following command in your terminal. It defaults to using the `Streamable HTTP` transport on port `8000`.

```bash
uv run modbus-mcp
```

To confirm the server is up and running and explore available resources and tools, run the [MCP Inspector](https://modelcontextprotocol.io/docs/tools/inspector) and connect it to the Modbus MCP server at `http://127.0.0.1:8000/mcp/`. Make sure to set the transport to `Streamable HTTP`.

```bash
npx @modelcontextprotocol/inspector
```

![s01](https://github.com/user-attachments/assets/e3673921-0396-4561-8640-884e9cef609a)


## Core Concepts

The Modbus MCP server leverages FastMCP 2.0's core building blocks - resource templates, tools, and prompts - to streamline Modbus read and write operations with minimal boilerplate and a clean, Pythonic interface.

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
