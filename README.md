## Modbus MCP Server

A lightweight [Model Context Protocol (MCP)](https://modelcontextprotocol.io) server that connects LLM agents to Modbus devices in a secure, standardized way, enabling seamless integration of AI-driven workflows with Building Automation (BAS) and Industrial Control (ICS) systems, allowing agents to monitor real-time sensor data, actuate devices, and orchestrate complex automation tasks.

[![test](https://github.com/ezhuk/modbus-mcp/actions/workflows/test.yml/badge.svg)](https://github.com/ezhuk/modbus-mcp/actions/workflows/test.yml)

## Getting Started

The server is built with [FastMCP 2.0](https://gofastmcp.com/getting-started/welcome) and uses [uv](https://github.com/astral-sh/uv) for project and dependency management. Simply run the following command to install `uv` or check out the [installation guide](https://docs.astral.sh/uv/getting-started/installation/) for more details and alternative installation methods.

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Clone the repository and use `uv` to install project dependencies and create a virtual environment.

```bash
git clone https://github.com/ezhuk/modbus-mcp.git
cd modbus-cmp
uv sync
```

Run the Modbus MCP server from the command line as follows. By default, it uses the Streamable HTTP transport on port `8000`.

```bash
uv run modbus-mcp
```

To confirm the server is up and running and explore available resources and tools, run the [MCP Inspector](https://modelcontextprotocol.io/docs/tools/inspector), go to `http://127.0.0.1:6274/` in your browser and connect it to the Modbus MCP server at `http://127.0.0.1:8000/mcp/`.

```bash
npx @modelcontextprotocol/inspector
```

## Core Concepts

TBD

## License

The server is licensed under the [MIT License](https://github.com/ezhuk/modbus-mcp?tab=MIT-1-ov-file).
