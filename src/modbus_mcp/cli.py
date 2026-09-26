import asyncio

import typer

from modbus_mcp.server import ModbusMCP

app = typer.Typer(
    name="modbus-mcp",
    help="ModbusMCP CLI",
)


@app.command()
def run(
    host: str | None = typer.Option(None, "--host"),
    port: int | None = typer.Option(None, "--port"),
):
    server = ModbusMCP()
    asyncio.run(server.run_async(transport="http", host=host, port=port))
