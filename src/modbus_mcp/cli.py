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
    kwargs: dict[str, object] = {}
    if host is not None:
        kwargs["host"] = host
    if port is not None:
        kwargs["port"] = port
    server = ModbusMCP()
    asyncio.run(server.run_async(transport="http", **kwargs))
